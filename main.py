import pandas as pd
import networkx as nx
import time

def group_students(preferences_file='preferences.csv', roster_file='roster.csv'):
    start_time = time.time()
    
    preferences_df = pd.read_csv(preferences_file)
    roster_df = pd.read_csv(roster_file)
    
    students = roster_df['Name'].tolist()
    student_set = set(students)
    num_students = len(students)
    total_groups = 6
    
    base_group_size = num_students // total_groups
    extra_students = num_students % total_groups
    group_sizes = [base_group_size + 1 if i < extra_students else base_group_size for i in range(total_groups)]
    
    preference_ranks = {
        1: 5,
        2: 4,
        3: 3,
        4: 2,
        5: 1
    }

    # my attempt to find a balance between mutual preferences and group size
    def calculate_weight(rank_a, rank_b):
        if rank_a >= 4 and rank_b >= 4:
            return 10  
        elif (rank_a >= 4 and rank_b == 0) or (rank_b >= 4 and rank_a == 0):
            return 1
        elif rank_a <= 2 and rank_b <= 2 and rank_a > 0 and rank_b > 0:
            return 5
        else:
            return rank_a + rank_b

    G = nx.Graph()
    G.add_nodes_from(students)

    # Build the weighted edges based on preferences
    # Map each student's preferences to ranks
    student_preferences = {}
    for student in students:
        student_preferences[student] = {}  # Initialize preferences

    # Fill in the preferences for students who submitted them
    for idx, row in preferences_df.iterrows():
        student = row['I am _____ (your name)']
        if student not in student_set:
            continue  # Skip students not in roster
        prefs = {}
        for pref_num in range(1, 6):
            pref_student = row.get(f'Preference {pref_num}')
            if pd.notna(pref_student) and pref_student in student_set:
                rank = preference_ranks[pref_num]
                prefs[pref_student] = rank
        student_preferences[student] = prefs

    # Add edges with weights to the graph
    for student_a in students:
        prefs_a = student_preferences.get(student_a, {})
        for student_b in students:
            if student_a == student_b:
                continue
            prefs_b = student_preferences.get(student_b, {})
            rank_ab = prefs_a.get(student_b, 0)
            rank_ba = prefs_b.get(student_a, 0)
            if rank_ab == 0 and rank_ba == 0:
                continue  # No preference between these students
            weight = calculate_weight(rank_ab, rank_ba)
            G.add_edge(student_a, student_b, weight=weight)

    # modified greedy algorithm that accounts for mutual preferences
    # Sort edges by weight in descending order
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)

    assigned_students = set()
    groups = [set() for _ in range(total_groups)]
    group_indices = list(range(total_groups))
    group_sizes_map = {i: size for i, size in enumerate(group_sizes)}

    # Keep track of which group each student is assigned to
    student_group_map = {}

    # Assign students based on sorted edges
    for edge in sorted_edges:
        if time.time() - start_time > 50:
            break  # time limit
        s1, s2, data = edge
        if s1 in assigned_students and s2 in assigned_students:
            continue  # Both students already assigned
        weight = data['weight']
        # Find or create groups for s1 and s2
        s1_group_idx = student_group_map.get(s1)
        s2_group_idx = student_group_map.get(s2)

        # Helper function to add student to group if possible
        def add_student_to_group(student, group_idx):
            group = groups[group_idx]
            if len(group) < group_sizes_map[group_idx]:
                group.add(student)
                student_group_map[student] = group_idx
                assigned_students.add(student)
                return True
            return False

        if s1_group_idx is not None and s2_group_idx is not None:
            if s1_group_idx != s2_group_idx:
                # Cannot merge groups if it exceeds group size
                group1_size = len(groups[s1_group_idx])
                group2_size = len(groups[s2_group_idx])
                total_size = group1_size + group2_size
                max_group_size = max(group_sizes_map[s1_group_idx], group_sizes_map[s2_group_idx])
                if total_size <= max_group_size:
                    # Merge groups
                    groups[s1_group_idx].update(groups[s2_group_idx])
                    for student in groups[s2_group_idx]:
                        student_group_map[student] = s1_group_idx
                    groups[s2_group_idx].clear()
                else:
                    continue  # Cannot merge groups
        elif s1_group_idx is not None:
            add_student_to_group(s2, s1_group_idx)
        elif s2_group_idx is not None:
            add_student_to_group(s1, s2_group_idx)
        else:
            # Assign to the group with the most available space
            available_groups = sorted(group_indices, key=lambda idx: group_sizes_map[idx] - len(groups[idx]), reverse=True)
            for idx in available_groups:
                if add_student_to_group(s1, idx):
                    add_student_to_group(s2, idx)
                    break

    unassigned_students = student_set - assigned_students
    for student in unassigned_students:
        placed = False
        prefs = student_preferences.get(student, {})
        # Try to place the student in a group with preferred peers
        preferred_groups = set()
        for pref_student in prefs.keys():
            pref_group_idx = student_group_map.get(pref_student)
            if pref_group_idx is not None:
                preferred_groups.add(pref_group_idx)
        for group_idx in preferred_groups:
            if len(groups[group_idx]) < group_sizes_map[group_idx]:
                groups[group_idx].add(student)
                student_group_map[student] = group_idx
                assigned_students.add(student)
                placed = True
                break
        if not placed:
            # Assign to any group with available spots
            for idx in group_indices:
                if len(groups[idx]) < group_sizes_map[idx]:
                    groups[idx].add(student)
                    student_group_map[student] = idx
                    assigned_students.add(student)
                    break

    # Remove empty groups
    groups = [group for group in groups if group]

    for idx, group in enumerate(groups):
        expected_size = group_sizes_map[idx]
        actual_size = len(group)
        if actual_size != expected_size:
            # Adjust groups to match expected sizes
            # Find students to move from overfull groups to underfull groups
            if actual_size > expected_size:
                # Move extra students to groups that need students
                extra_students = list(group)[expected_size:]
                group = set(list(group)[:expected_size])
                groups[idx] = group
                for student in extra_students:
                    student_group_map.pop(student, None)
                    assigned_students.remove(student)
                # Reassign the removed students
                for student in extra_students:
                    for other_idx in group_indices:
                        if len(groups[other_idx]) < group_sizes_map[other_idx]:
                            groups[other_idx].add(student)
                            student_group_map[student] = other_idx
                            assigned_students.add(student)
                            break

    for idx, group in enumerate(groups):
        group_list = list(group)
        names = sorted([member.split(', ')[1] for member in group_list])
        print(f"Group {idx + 1} (Size {len(group)}): {', '.join(names)}")

    end_time = time.time()
    print(f"Algorithm completed in {end_time - start_time:.2f} seconds.")

group_students('preferences.csv', 'roster.csv')
