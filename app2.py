import streamlit as st
import random
import time

# ===== GAME SETUP =====
if 'game' not in st.session_state:
    st.session_state.game = {
        'hp': 100,
        'max_hp': 100,
        'mana': 50,
        'max_mana': 50,
        'score': 0,
        'inventory': [],
        'location': 'field',
        'wand_color': random.choice(['blue', 'green', 'red', 'purple', 'gold']),
        'enemy': None,
        'game_over': False
    }

# Game data
enemies = {
    'goblin': {'hp': 30, 'damage': (5, 15), 'score': 10, 'image': '👺'},
    'troll': {'hp': 50, 'damage': (10, 20), 'score': 20, 'image': '🧌'},
    'pirate': {'hp': 40, 'damage': (8, 18), 'score': 15, 'image': '🏴‍☠️'},
    'wicked fairy': {'hp': 70, 'damage': (15, 25), 'score': 100, 'image': '🧚'}
}

spells = {
    'fireball': {'damage': (15, 30), 'cost': 10, 'icon': '🔥'},
    'lightning': {'damage': (20, 35), 'cost': 15, 'icon': '⚡'},
    'heal': {'effect': 25, 'cost': 20, 'icon': '💚'},
    'shield': {'defense': 0.5, 'cost': 10, 'icon': '🛡️'}
}

items = {
    'potion': {'effect': 50, 'cost': 30, 'icon': '🧪'},
    'key': {'use': 'dungeon', 'cost': 40, 'icon': '🗝️'},
    'swim_ring': {'use': 'river', 'cost': 20, 'icon': '🛟'}
}

# ===== CORE FUNCTIONS =====
def reset_game():
    st.session_state.game = {
        'hp': 100,
        'max_hp': 100,
        'mana': 50,
        'max_mana': 50,
        'score': 0,
        'inventory': [],
        'location': 'field',
        'wand_color': random.choice(['blue', 'green', 'red', 'purple', 'gold']),
        'enemy': None,
        'game_over': False
    }

def show_status():
    g = st.session_state.game
    st.sidebar.markdown(f"""
    ### 🧙 Player Stats
    **HP**: {g['hp']}/{g['max_hp']}  
    **Mana**: {g['mana']}/{g['max_mana']}  
    **Score**: {g['score']}  
    **Wand**: {g['wand_color'].capitalize()}  
    
    ### 🎒 Inventory
    {', '.join([f"{items[item]['icon']} {item}" for item in g['inventory']]) or "Empty"}
    """)

def use_item(item):
    g = st.session_state.game
    if item == 'potion':
        g['hp'] = min(g['max_hp'], g['hp'] + items['potion']['effect'])
        st.success(f"Used {items['potion']['icon']} potion! +50 HP")
    elif item == 'key':
        st.warning("The key shines but has no use here.")
    elif item == 'swim_ring':
        st.warning("The swim ring floats gently.")
    g['inventory'].remove(item)

def cast_spell(spell_name):
    g = st.session_state.game
    spell = spells[spell_name]
    
    if g['mana'] < spell['cost']:
        st.error("Not enough mana!")
        return False
    
    g['mana'] -= spell['cost']
    
    if spell_name in ['fireball', 'lightning']:
        damage = random.randint(*spell['damage'])
        g['enemy']['hp'] -= damage
        st.success(f"{spell['icon']} You hit for {damage} damage!")
    elif spell_name == 'heal':
        g['hp'] = min(g['max_hp'], g['hp'] + spell['effect'])
        st.success(f"{spell['icon']} Healed for {spell['effect']} HP!")
    elif spell_name == 'shield':
        st.success(f"{spell['icon']} Damage reduced next attack!")
    
    return True

def enemy_turn():
    g = st.session_state.game
    if g['enemy']:
        enemy = enemies[g['enemy']['type']]
        damage = random.randint(*enemy['damage'])
        
        # Shield reduces damage
        if 'shield' in [action.split()[0] for action in st.session_state.get('last_actions', [])]:
            damage = int(damage * 0.5)
        
        g['hp'] -= damage
        st.error(f"{enemy['image']} {g['enemy']['type'].title()} hits you for {damage} damage!")
        
        if g['hp'] <= 0:
            g['hp'] = 0
            g['game_over'] = True
            st.error("💀 YOU DIED!")
            return False
    return True

# ===== LOCATIONS =====
def field():
    g = st.session_state.game
    g['location'] = 'field'
    g['enemy'] = None
    
    st.markdown("""
    ## 🌾 The Field
    You stand in an open field filled with wildflowers. 
    The wind carries whispers of adventure.
    """)
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("🏠 House"):
            house()
    with cols[1]:
        if st.button("🕳️ Cave"):
            cave()
    with cols[2]:
        if st.button("🌊 River"):
            river()
    with cols[3]:
        if st.button("🧙 Witch's Hut"):
            witch_hut()

def house():
    g = st.session_state.game
    g['location'] = 'house'
    
    st.markdown("## 🏠 The Old House")
    if random.random() > 0.4:  # 60% chance of encounter
        enemy_type = random.choice(['goblin', 'troll', 'pirate'])
        g['enemy'] = {'type': enemy_type, 'hp': enemies[enemy_type]['hp']}
        st.warning(f"{enemies[enemy_type]['image']} A {enemy_type} attacks!")
        combat()
    else:
        st.write("The house is eerily quiet...")
        if st.button("🔙 Return to Field"):
            field()

def cave():
    g = st.session_state.game
    g['location'] = 'cave'
    
    st.markdown("## 🕳️ The Dark Cave")
    if 'torch' not in g['inventory']:
        st.error("It's too dark to explore without light!")
    else:
        if random.random() > 0.7:  # 30% chance of treasure
            loot = random.choice(['potion', 'key'])
            g['inventory'].append(loot)
            st.success(f"✨ You found a {items[loot]['icon']} {loot}!")
        else:
            st.write("You find nothing but damp walls.")
    
    if st.button("🔙 Return to Field"):
        field()

# (Add river(), dungeon(), witch_hut() following similar patterns)

# ===== COMBAT SYSTEM =====
def combat():
    g = st.session_state.game
    enemy = g['enemy']
    
    st.markdown(f"""
    ## ⚔️ Combat
    {enemies[enemy['type']]['image']} {enemy['type'].title()}
    HP: {enemy['hp']}/{enemies[enemy['type']]['hp']}
    """)
    
    # Spell buttons
    cols = st.columns(4)
    for i, (spell, data) in enumerate(spells.items()):
        with cols[i]:
            if st.button(f"{data['icon']} {spell.capitalize()}"):
                if cast_spell(spell):
                    if enemy['hp'] <= 0:
                        st.success(f"🎉 You defeated the {enemy['type']}!")
                        g['score'] += enemies[enemy['type']]['score']
                        if random.random() > 0.5:  # 50% chance of loot
                            loot = random.choice(['potion', 'key'])
                            g['inventory'].append(loot)
                            st.success(f"✨ Found {items[loot]['icon']} {loot}!")
                        field()
                        return
                    enemy_turn()
    
    # Item buttons
    if g['inventory']:
        with st.expander("🎒 Use Item"):
            for item in g['inventory']:
                if st.button(f"{items[item]['icon']} {item.capitalize()}"):
                    use_item(item)
                    enemy_turn()
    
    # Flee button
    if st.button("🏃‍♂️ Flee"):
        if random.random() > 0.7:  # 30% chance to flee
            st.success("You escaped safely!")
            field()
        else:
            st.error("You couldn't escape!")
            enemy_turn()

# ===== MAIN APP =====
def main():
    st.set_page_config(page_title="Isekai Adventure", page_icon="🎮")
    
    # Title and reset
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("✨ Isekai Adventure")
    with col2:
        if st.button("🔄 New Game"):
            reset_game()
    
    # Game over screen
    if st.session_state.game['game_over']:
        st.error("## 💀 Game Over")
        st.write(f"Final Score: {st.session_state.game['score']}")
        if st.button("🔄 Try Again"):
            reset_game()
        return
    
    # Show current location
    show_status()
    {
        'field': field,
        'house': house,
        'cave': cave,
        # Add other locations here
    }[st.session_state.game['location']]()

if __name__ == "__main__":
    main()