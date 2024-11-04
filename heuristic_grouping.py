import pandas as pd

def load_data(preferences_file, roster_file):
    preferences = pd.read_csv(preferences_file)
    roster = pd.read_csv(roster_file)
    
    valid_names = set(roster['Name'])
    preferences = preferences[preferences['I am _____ (your name)'].isin(valid_names)]
    
    # Create preference mappings
    preference_dict = {}
    for index, row in preferences.iterrows():
        name = row['I am _____ (your name)']
        # Filter and order preferences to ensure they are valid
        listed_preferences = [row[f'Preference {i}'] for i in range(1, 6)
                              if pd.notna(row[f'Preference {i}']) and row[f'Preference {i}'] in valid_names]
        preference_dict[name] = listed_preferences
    
    return preference_dict, list(valid_names)

def heuristic_grouping(preference_dict, all_people, max_group_size):
    groups = []
    unassigned = set(all_people)
    
    while unassigned:
        group = []
        # Select the person with the most preferences not yet assigned
        person = max(unassigned, key=lambda p: len([q for q in preference_dict.get(p, []) if q in unassigned]))
        group.append(person)
        unassigned.remove(person)
        
        # Try to add preferred people to the group
        for pref in preference_dict.get(person, []):
            if pref in unassigned and len(group) < max_group_size:
                group.append(pref)
                unassigned.remove(pref)
        
        # Fill the group with others if necessary
        while len(group) < max_group_size and unassigned:
            next_person = unassigned.pop()
            group.append(next_person)
        
        groups.append(group)
    
    group_assignments = {f'Group {i+1}': group for i, group in enumerate(groups)}
    return group_assignments

preference_dict, all_people = load_data('preferences.csv', 'roster.csv')

max_group_size = 5

group_assignments = heuristic_grouping(preference_dict, all_people, max_group_size)

print("\nFinal Group Assignments:")
for group, members in group_assignments.items():
    names = sorted([member.split(', ')[1] for member in members])
    print(f'{group}: {", ".join(names)}')
