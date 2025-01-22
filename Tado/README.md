# Tado: A CustomTkinter Todo App with Weather Integration

Tado is a desktop to-do list application built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) that allows users to manage daily tasks while displaying current weather information. The application supports adding, editing, completing, and organizing tasks across different days of the week. It also fetches the current temperature based on the user's approximate location using the [Open-Meteo API](https://open-meteo.com/) and [ipapi.co](https://ipapi.co/).

## Features

- **Day-Based Task Management**: Manage separate tasks for each day of the week.
- **Add, Edit, and Complete Tasks**: Easily add new tasks, edit existing ones, and mark them as completed.
- **Persistent Storage**: Tasks and weather data are saved locally to a JSON file (`tasks.json`) and loaded upon startup.
- **Weather Integration**: Fetches and displays the current temperature for the user's location.
- **Responsive UI**: A scrollable list of tasks with a fixed header and day blocks for smooth navigation.
- **Dark Mode & Custom Themes**: Built with CustomTkinter to provide a modern, dark-themed interface.

**Install dependencies:**

   ```bash
   pip install customtkinter requests
   ```

   Make sure you have Python 3.7+ installed.

## Running the App

To launch Tado, simply run:

```bash
python tado.py
```

This will open the desktop application window where you can manage your tasks and view weather updates.

## Code Structure

The main script is organized as follows:

```
├── tado.py            # Main application file with the TodoApp class
├── tasks.json         # JSON file used for saving tasks and weather data
├── README.md          # This readme file
```

### `main.py`

- **Imports**: 
  - CustomTkinter for the UI
  - `datetime`, `json`, `os`, and `requests` for functionality
  - `Thread` and `partial` for threading and event binding

- **`TodoApp` Class**:
  - Inherits from `ctk.CTk` and initializes the UI.
  - **UI Components**:
    - **Header**: Displays the current day, date, time, and temperature.
    - **Task Input**: Allows adding new tasks.
    - **Scrollable Task List**: Displays tasks for the selected day.
    - **Day Blocks**: Buttons at the bottom to switch between days.
  - **Weather Functions**:
    - `get_location()`: Retrieves user's approximate latitude and longitude.
    - `fetch_weather()`: Fetches temperature data from the Open-Meteo API.
    - `update_weather()` and `update_clock()`: Periodically update the UI.
  - **Task Management Functions**:
    - `add_task()`, `edit_task()`, `save_edited_task()`, `toggle_task()`: Manage task actions.
    - `save_tasks()` and `load_tasks()`: Persist tasks and weather data to/from `tasks.json`.
  - **Day Switching**: `switch_day()` to change the current day and refresh tasks.

## Dependencies

- [CustomTkinter](https://pypi.org/project/CustomTkinter/): For modern Tkinter-based UI.
- [requests](https://pypi.org/project/requests/): To fetch data from external APIs.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and create a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

Enjoy managing your tasks with Tado while staying updated on the weather! ☀️☁️🌧️