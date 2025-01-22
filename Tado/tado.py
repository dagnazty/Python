import customtkinter as ctk
from datetime import datetime
import json
import os
import requests
from threading import Thread
from functools import partial

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tado")
        self.geometry("350x700")
        self.resizable(False, False)

        # Weather data
        self.temperature = "Loading..."
        self.last_weather_update = None

        self.days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        self.tasks = {day: [] for day in self.days}
        self.load_tasks()
        self.current_day = "MONDAY"

        # Create main UI components
        self.create_fixed_header()
        self.create_task_input()
        self.create_scrollable_tasks()
        self.create_day_blocks()

        # Start updates
        self.update_clock()
        self.update_weather()

    def create_fixed_header(self):
        """Fixed header at top with day and weather"""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(10, 0))

        self.day_label = ctk.CTkLabel(
            self.header_frame,
            text=self.current_day,
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        self.day_label.pack(anchor="w")

        self.date_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=("Helvetica", 14),
            text_color="#AAAAAA"
        )
        self.date_label.pack(anchor="w", pady=(0, 15))

    def create_task_input(self):
        """Fixed task input section below header"""
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.task_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter new task...",
            width=250,
            height=35
        )
        self.task_entry.pack(side="left", padx=(0, 5))

        self.add_btn = ctk.CTkButton(
            self.input_frame,
            text="Add",
            width=60,
            height=35,
            command=self.add_task
        )
        self.add_btn.pack(side="left")

    def create_scrollable_tasks(self):
        """Scrollable area for tasks only"""
        self.tasks_scrollable = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            scrollbar_button_color="#2B2B2B",
            scrollbar_button_hover_color="#2B2B2B"
        )
        self.tasks_scrollable.pack(fill="both", expand=True, padx=5)
        
        self.tasks_container = ctk.CTkFrame(self.tasks_scrollable, fg_color="transparent")
        self.tasks_container.pack(fill="x")
        self.show_day_tasks(self.current_day)

    def create_scrollable_area(self):
        """Create scrollable area for tasks and header"""
        # Scrollable Frame with hidden scrollbar
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            scrollbar_button_color="#2B2B2B",  # Match dark background
            scrollbar_button_hover_color="#2B2B2B"  # Remove hover effect
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Header Section
        self.header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(10, 0))

        self.day_label = ctk.CTkLabel(
            self.header_frame,
            text=self.current_day,
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        self.day_label.pack(anchor="w", padx=15)

        self.date_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=("Helvetica", 14),
            text_color="#AAAAAA"
        )
        self.date_label.pack(anchor="w", padx=15, pady=(0, 15))

        # Task Input Section
        self.input_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=(0, 10))
        
        self.task_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter new task...",
            width=250,
            height=35
        )
        self.task_entry.pack(side="left", padx=(0, 5))
        
        self.add_btn = ctk.CTkButton(
            self.input_frame,
            text="Add",
            width=60,
            height=35,
            command=self.add_task
        )
        self.add_btn.pack(side="left")

        # Tasks Container
        self.tasks_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.tasks_container.pack(fill="x")
        self.show_day_tasks(self.current_day)

    def get_location(self):
        """Get approximate location using IP address"""
        try:
            response = requests.get("https://ipapi.co/json/", timeout=5)
            data = response.json()
            return data["latitude"], data["longitude"]
        except:
            return None, None

    def fetch_weather(self):
        """Fetch temperature using Open-Meteo API"""
        try:
            lat, lon = self.get_location()
            if lat and lon:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&temperature_unit=fahrenheit"
                response = requests.get(url, timeout=5)
                data = response.json()
                self.temperature = f"{data['current']['temperature_2m']}°F"
            else:
                self.temperature = "N/A°F"
            self.last_weather_update = datetime.now()
        except Exception as e:
            print(f"Weather error: {e}")
            self.temperature = "N/A°F"

    def update_weather(self):
        """Update weather in background thread only if data is stale"""
        needs_update = True
        if self.last_weather_update:
            needs_update = (datetime.now() - self.last_weather_update).seconds >= 3600
        
        if needs_update:
            Thread(target=self.fetch_weather, daemon=True).start()
        
        self.after(60000, self.update_weather)  # Check every minute

    def update_clock(self):
        """Update time and temperature display"""
        now = datetime.now()
        time_str = now.strftime("%B %d %Y – %I:%M%p – ") + self.temperature
        self.date_label.configure(text=time_str)
        self.after(60000, self.update_clock)

    def create_main_container(self):
        """Create main layout with fixed header and scrollable tasks"""
        # Main container (not scrollable)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Fixed Header Section
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(10, 0))

        self.day_label = ctk.CTkLabel(
            self.header_frame,
            text=self.current_day,
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        self.day_label.pack(anchor="w", padx=15)

        self.date_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=("Helvetica", 14),
            text_color="#AAAAAA"
        )
        self.date_label.pack(anchor="w", padx=15, pady=(0, 15))

        # Task Input Section (fixed)
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=(0, 10))
        
        self.task_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter new task...",
            width=250,
            height=35
        )
        self.task_entry.pack(side="left", padx=(0, 5))
        
        self.add_btn = ctk.CTkButton(
            self.input_frame,
            text="Add",
            width=60,
            height=35,
            command=self.add_task
        )
        self.add_btn.pack(side="left")

        # Scrollable Tasks Area
        self.tasks_scrollable = ctk.CTkScrollableFrame(
            self.main_frame,
            corner_radius=0,
            scrollbar_button_color="#2B2B2B",
            scrollbar_button_hover_color="#2B2B2B"
        )
        self.tasks_scrollable.pack(fill="both", expand=True)

        # Tasks Container inside scrollable area
        self.tasks_container = ctk.CTkFrame(self.tasks_scrollable, fg_color="transparent")
        self.tasks_container.pack(fill="x")

        # Day Blocks at Bottom (fixed)
        self.day_blocks_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.day_blocks_frame.pack(fill="x", pady=5)

        self.show_day_tasks(self.current_day)
        self.create_day_blocks()

    def create_day_blocks_container(self):
        """Create fixed container at bottom for day blocks"""
        self.day_blocks_container = ctk.CTkFrame(self, fg_color="transparent")
        self.day_blocks_container.pack(side="bottom", fill="x", padx=5, pady=5)
        self.create_day_blocks()

    def create_day_blocks(self):
        """Fixed day blocks at bottom"""
        self.day_blocks_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.day_blocks_frame.pack(fill="x", padx=5, pady=5)
        
        # Grid layout with 2 columns
        grid_frame = ctk.CTkFrame(self.day_blocks_frame, fg_color="transparent")
        grid_frame.pack()
        
        left_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        left_col.pack(side="left", fill="x", expand=True)
        right_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
        right_col.pack(side="right", fill="x", expand=True)

        # Add day blocks to columns
        columns = [left_col, right_col]
        for idx, day in enumerate(self.days):
            if day == self.current_day:
                continue
                
            block = ctk.CTkFrame(
                columns[idx % 2],
                height=60,
                fg_color="#2B2B2B"
            )
            block.pack(fill="x", pady=2, padx=2)
            
            label = ctk.CTkLabel(
                block,
                text=day,
                font=("Helvetica", 14, "bold"),
                anchor="w"
            )
            label.pack(side="left", padx=10)
            
            # Bind click events using partial
            for widget in [block, label]:
                widget.bind("<Button-1>", partial(self.switch_day, day))

    def switch_day(self, new_day, event=None):
        """Handle day switching with proper refresh"""
        if new_day != self.current_day:
            self.current_day = new_day
            self.day_label.configure(text=new_day)
            self.show_day_tasks(new_day)
            # Rebuild day blocks
            self.day_blocks_frame.destroy()
            self.create_day_blocks()

    def show_day_tasks(self, day):
        """Show tasks for specified day"""
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        
        for idx, task in enumerate(self.tasks[day]):
            task_frame = ctk.CTkFrame(self.tasks_container, fg_color="#2B2B2B")
            task_frame.pack(fill="x", pady=2)

            # Checkbox
            checkbox = ctk.CTkCheckBox(
                task_frame,
                text="",
                width=30,
                command=partial(self.toggle_task, idx)
            )
            checkbox.pack(side="left", padx=10)
            if task["completed"]:
                checkbox.select()

            # Task text
            text_color = "#666666" if task["completed"] else "#FFFFFF"
            font_style = ("Helvetica", 14, "overstrike" if task["completed"] else "normal")
            
            ctk.CTkLabel(
                task_frame,
                text=task["text"],
                font=font_style,
                text_color=text_color,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            # Edit button
            ctk.CTkButton(
                task_frame,
                text="✎",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#444444",
                command=partial(self.edit_task, idx)
            ).pack(side="right", padx=5)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            self.tasks[self.current_day].append({"text": task_text, "completed": False})
            self.task_entry.delete(0, "end")
            self.show_day_tasks(self.current_day)
            self.save_tasks()

    def edit_task(self, task_index):
        # Grab the task to edit
        task = self.tasks[self.current_day][task_index]
        
        # Create a small edit frame in the tasks container
        edit_frame = ctk.CTkFrame(self.tasks_container, fg_color="#3A3A3A")
        edit_frame.pack(fill="x", pady=2)
        
        # Entry field for editing
        edit_entry = ctk.CTkEntry(
            edit_frame,
            width=250,
            height=35,
            font=("Helvetica", 14)
        )
        edit_entry.insert(0, task["text"])
        edit_entry.pack(side="left", padx=10, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            edit_frame,
            text="Save",
            width=60,
            height=35,
            command=lambda: self.save_edited_task(task_index, edit_entry.get(), edit_frame)
        )
        save_btn.pack(side="left", padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            edit_frame,
            text="×",
            width=30,
            height=35,
            fg_color="#FF4444",
            hover_color="#CC0000",
            command=lambda: edit_frame.destroy()
        )
        cancel_btn.pack(side="left")

    def save_edited_task(self, task_index, new_text, edit_frame):
        if new_text.strip():
            # Update task text if not empty
            self.tasks[self.current_day][task_index]["text"] = new_text.strip()
        else:
            # Delete task if input is empty
            self.tasks[self.current_day].pop(task_index)
        
        self.show_day_tasks(self.current_day)
        self.save_tasks()
        edit_frame.destroy()

    def toggle_task(self, task_index):
        task = self.tasks[self.current_day][task_index]
        task["completed"] = not task["completed"]
        self.show_day_tasks(self.current_day)
        self.save_tasks()

    def save_tasks(self):
        """Save tasks and weather data to JSON file"""
        data = {
            "tasks": self.tasks,
            "weather": {
                "temperature": self.temperature,
                "last_update": datetime.now().isoformat()
            }
        }
        with open("tasks.json", "w") as f:
            json.dump(data, f, indent=2)

    def load_tasks(self):
        """Load tasks and weather data from JSON file"""
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r") as f:
                    data = json.load(f)
                    
                    # Load tasks
                    for day in self.days:
                        self.tasks[day] = [
                            t if isinstance(t, dict) 
                            else {"text": t, "completed": False}
                            for t in data.get("tasks", {}).get(day, [])
                        ]
                    
                    # Load weather data if available and valid
                    weather_data = data.get("weather", {})
                    if weather_data:
                        # Handle empty timestamp gracefully
                        if weather_data.get("last_update"):
                            try:
                                last_update = datetime.fromisoformat(weather_data["last_update"])
                                # Only use if less than 1 hour old
                                if (datetime.now() - last_update).seconds < 3600:
                                    self.temperature = weather_data.get("temperature", "N/A°F")
                                    self.last_weather_update = last_update
                            except ValueError:
                                print("Invalid timestamp format, ignoring saved weather data")
                        else:
                            print("No timestamp found in weather data")
                            
            except Exception as e:
                print(f"Error loading data: {e}")

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
