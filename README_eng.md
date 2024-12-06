[**中文**](README.md)  
A plugin for player behavior logging and query, compatible with the Endstone plugin loader.

# Feature Overview

## Behavior Logging

The Tianyan plugin uses Endstone's event API to record behavior events. It supports logging the following types of behavior events:

### Container Interaction and Other Interaction Events

Logs player interactions with containers like chests, trapped chests, shulker boxes, ender chests, barrels, furnaces, blast furnaces, hoppers, dispensers, and droppers. It also records player interactions with blocks using items like flint and steel, lava buckets, fire charges, water buckets (including buckets with mobs), and powdered snow buckets. Interactions with beds and respawn anchors are also recorded.

### Block Destruction Events

- **When only artificial blocks are logged:** Records the destruction of all player-placed blocks and certain natural blocks (cannot log farmland trampled by players).  
- **When logging all blocks:** Records all block destruction events caused by players (trampling farmland still cannot be logged).

### Entity Hit Events

- **When logging only important entities:** Logs hit events for specific entities such as horses, pigs, wolves, cats, sniffers, parrots, donkeys, mules, and villagers (even if not hit by a player).  
- **When logging all entities:** Logs all hit events for all entities, including attacks by players, entity attacks on players, and attacks by non-player entities.

### Entity Interaction Events

Logs all interactions between players and entities.

### Block Placement Events

Logs all block placement events performed directly by players.

## Player Information Display and Ban Features

### Player Join Information Display

The Tianyan plugin displays player system names and device IDs when they join the server.

### Ban and Anti-Spam Features

- **Ban Players by Name:** Prevent specific players from joining the server.  
- **Ban Players by Device ID:** Blocks any player using a banned device (with the same device ID) from joining the server.  
- **Anti-Spam:** Automatically bans players who send excessive messages (more than 6 within 10 seconds) or commands (more than 12 within 10 seconds). An administrator must be contacted to lift the ban.

# Installation, Configuration, and Usage

## Installing Endstone

Refer to the official Endstone documentation for installation instructions.

## Installing the Tianyan Plugin

Download the latest plugin version from the release section and place it in the `plugins` directory of the server. Start the server to activate the plugin.

## Configuring the Tianyan Plugin

After running the plugin, a `tianyan_data` folder will be created in the `plugins` directory. Inside, there is a configuration file named `config.json` with the following default configuration:

```json
{"Record natural blocks": true, "Record artificial blocks": true, "Record only significant entities": true}
```

- To log all entity hit events instead of just important ones, change `"Record only significant entities": true` to `"false"`.  
- The plugin defaults to Chinese but supports English via a language configuration file (`lang.json`). A pre-translated English configuration file made by ChatGPT is available for download in the release section.

## Plugin Command Usage

### Tianyan Commands

Use `/ty` to query player and entity behavior logs. Format:

```shell
/ty x y z time (hours) radius
```

Use `/tygui` to query logs using a graphical menu. Format:

```shell
/tygui
```

Use `/tys` to search for specific keywords. Format:

```shell
/tys search_type keyword time (hours)
```

- **Search types:** `player`, `action`, `object` (e.g., player name, action type, or target object).  
- **Keywords:** Examples include player names, action types (`interact`, `destroy`, `attack`, `place`), or object names (in-game IDs or Chinese terms for certain items like chests, hoppers, etc.).

Use `/tysgui` to perform keyword searches with a graphical menu. Format:

```shell
/tysgui
```

### Player Ban Commands

- **Ban a player:**  
  ```shell
  /tyban player_name reason (optional)
  ```  
- **Unban a player:**  
  ```shell
  /tyunban player_name
  ```  
- **List banned players:**  
  ```shell
  /tybanlist
  ```  
- **Ban a device:**  
  ```shell
  /banid device_id
  ```  
- **Unban a device:**  
  ```shell
  /unbanid device_id
  ```  
- **List banned devices:**  
  ```shell
  /banidlist
  ```  

### Experimental Features

- Use `/tyback` to restore block placement and destruction actions. Format:
  ```shell
  /tyback coordinates time (hours) radius player_name (optional)
  ```

## Development & Packaging

Ensure `endstone` and `pipx` are installed in your Python environment.

### Clone the Code

```shell
git clone https://github.com/yuhangle/endstone_TianyanPlugin.git
```

### Navigate to the Code Directory

```shell
cd endstone_TianyanPlugin
```

### Package the Plugin

```shell
pipx run build --wheel
```