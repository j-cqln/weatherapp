# Libraries
import requests
import country_converter

from configparser import ConfigParser

import datetime

import tkinter as tk
from tkinter import font
from tkinter import messagebox

class WeatherApp:
    """
    Class for the weatherapp application

    Creates a GUI weather application
    """
    ORANGE_BACKGROUND = '#d8ac8e'
    BLUE_BACKGROUND = '#8ebcd8'
    PURPLE_BACKGROUND = '#928ed8'
    ENTRY_BACKGROUND = '#ffffff'
    BUTTON_BACKGROUND = '#ffffff'
    ENTRY_TEXT = '#000000'
    PROMPT_TEXT = '#959595'
    DISPLAY_TEXT = '#000000'

    def __init__(self):
        """
        Initializes the WeatherApp class
        """
        # Parse configuration file
        self._config_file = 'config.ini'

        self._config = ConfigParser()
        self._config.read(self._config_file)
        self._api_key = self._config['Default']['api']

        # OpenWeatherMap URL
        self._url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

        # GUI
        self._root = tk.Tk()
        self._root.title('weatherapp')
        self._root.geometry('300x400')
        self._root.minsize(300, 400)
        self._root.maxsize(300, 400)

        # Font
        self._root.option_add('*Font', 'helvetica')
        self._default_font = tk.font.Font(family='helvetica', size=8)
        self._location_font = tk.font.Font(family='helvetica', size=10)
        self._coords_font = tk.font.Font(family='helvetica', size=8)
        self._current_temp_font = tk.font.Font(family='helvetica', size=14)
        self._max_min_font = tk.font.Font(family='helvetica', size=8)

        self._root.rowconfigure(0, weight=0)
        self._root.rowconfigure(1, weight=1)
        self._root.rowconfigure(2, weight=0)

        self._root.columnconfigure(0, weight=1)
        self._root.columnconfigure(1, weight=0)

        # For location entry
        self._city_text = tk.StringVar(self._root)
        self._city_entry = tk.Entry(self._root, textvariable=self._city_text, font=self._default_font, justify='left', borderwidth=0, highlightthickness=0)
        self._city_entry.insert(0, ' city name here...')
        self._city_entry.bind('<FocusIn>', self._city_entry_focus)
        self._city_entry.bind('<FocusOut>', self._city_entry_unfocus)
        self._city_entry.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky='NWSE')

        # Search button
        self._search_button = tk.Label(self._root, text=' > ', font=self._default_font, anchor='n', justify='center', borderwidth=0, highlightthickness=0)
        self._search_button.bind('<Button-1>', self._add_new_location)
        self._search_button.grid(row=0, column=1, padx=(0, 10), pady=(10, 10), sticky='NWSE')

        # Frame for location information
        self._city_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._city_frame.grid(row=1, column=0, sticky='NWSE')
        self._city_frame.grid_propagate(False)

        # Location information
        self._city_label = tk.Label(self._city_frame, text='', anchor='w', justify='left', font=self._location_font)
        self._city_label.grid(row=0, column=0, padx=(8, 10), sticky='NWSE')

        self._coords_label = tk.Label(self._city_frame, text='', anchor='w', justify='left', font=self._coords_font)
        self._coords_label.grid(row=1, column=0, padx=(8, 8), sticky='NWSE')

        self._temp_frame = tk.Frame(self._city_frame, borderwidth=0, highlightthickness=0)
        self._temp_frame.grid(row=2, column=0, sticky='NWSE')

        self._temp_frame.columnconfigure(0, weight=0)
        self._temp_frame.columnconfigure(1, weight=0)

        self._current_temp_label = tk.Label(self._temp_frame, text='', anchor='w', justify='left', font=self._current_temp_font)
        self._current_temp_label.grid(row=0, column=0, padx=(8, 0), sticky='NWSE')

        self._max_min_label = tk.Label(self._temp_frame, text='', anchor='sw', justify='left', font=self._max_min_font)
        self._max_min_label.grid(row=0, column=1, padx=(0, 8), sticky='NWSE')
        
        self._weather_label = tk.Label(self._city_frame, text='', anchor='w', justify='left', font=self._default_font)
        self._weather_label.grid(row=3, column=0, padx=(8, 8), sticky='NWSE')

        self._root.bind_all('<Button-1>', lambda event:event.widget.focus_set())

        # Set background color based on current time
        self._color_update(self._which_background(datetime.datetime.now().hour))

        # Application loop
        self._root.mainloop()
    
    def _city_entry_focus(self, *args):
        """
        Focus on the city entry widget, remove prompt text if it is displayed
        """
        if self._city_entry.get() == ' city name here...':
            self._city_entry.delete(1, tk.END)
            
        self._city_entry.config({'foreground': self.ENTRY_TEXT})

    def _city_entry_unfocus(self, *args):
        """
        Unfocus from the city entry widget, restoring prompt text if no text entered
        """
        if self._city_entry.get() == '' or self._city_entry.get() == ' ':
            self._city_entry.delete(0, tk.END)
            self._city_entry.insert(0, ' city name here...')

        self._city_entry.config({'foreground': self.PROMPT_TEXT})
        self._root.focus_set()

    def _which_background(self, hour):
        """
        Determinues which background color to use based on given time of day

        hour: hour, int
        """
        if hour < 5 or hour > 20:
            background_color = WeatherApp.PURPLE_BACKGROUND
        elif hour > 7 and hour < 17:
            background_color = WeatherApp.BLUE_BACKGROUND
        else:
            background_color = WeatherApp.ORANGE_BACKGROUND

        return background_color
    
    def _color_update(self, color, parent=None):
        """
        Updates colors for widget and all descendant widgets based on current theme mode

        color: hex color for widgets with dynamic background color, string
        parent: widget to change color for, tkinter widget
        """
        # If no widget provided, start at root
        if parent is None:
            parent = self._root
            parent.config({'background': color})

        # Change color for all descendant widgets
        for child in parent.winfo_children():
            if child.winfo_children():
                self._color_update(color, child)
            
            if type(child) is tk.Entry:
                child.config({'foreground': WeatherApp.PROMPT_TEXT})
                child.config({'background': WeatherApp.ENTRY_BACKGROUND})
            
            elif type(child) is tk.Label:
                if child is self._search_button:
                    child.config({'foreground': WeatherApp.DISPLAY_TEXT})
                    child.config({'background': WeatherApp.BUTTON_BACKGROUND})
                else:
                    child.config({'foreground': WeatherApp.DISPLAY_TEXT})
                    child.config({'background': color})
            
            elif type(child) is tk.Frame:
                child.config({'background': color})

    def _degrees_to_dms(self, lat, lon):
        """
        Convert latitude and longitude in decimal degrees to degrees, minutes, seconds

        lat: latitude, float
        lon: longitude, float
        """
        try:
            lat_d = int(lat)
            lat_md = abs(lat - lat_d) * 60
            lat_m = int(lat_md)
            lat_sd = (lat_md - lat_m) * 60
            lat_s = int(lat_sd)
            
            lon_d = int(lon)
            lon_md = abs(lon - lon_d) * 60
            lon_m = int(lon_md)
            lon_sd = (lon_md - lon_m) * 60
            lon_s = int(lon_sd)

            # Sign of result determines north/south or west/east
            if lat_d > 0:
                lat_dms = str(lat_d) + '°' + str(lat_m) + '\'' + str(lat_s) + '\'N'
            else:
                lat_dms = str(abs(lat_d)) + '°' + str(lat_m) + '\'' + str(lat_s) + '\'S'

            if lon_d > 0:
                lon_dms = str(lon_d) + '°' + str(lon_m) + '\'' + str(lon_s) + '\'E'
            else:
                lon_dms = str(abs(lon_d)) + '°' + str(lon_m) + '\'' + str(lon_s) + '\'W'

            dms = lat_dms + ', ' + lon_dms

            return dms
        except:
            messagebox.showerror('Error', 'Invalid longitude and latitude.')
            return None

    def _add_new_location(self, *args):
        """
        Add new location to weather application
        """
        # Retrieve user-entered location
        city = self._city_text.get().strip()

        # If not placeholder text, retrieve and display weather information
        if city != 'city name here...':
            weather = self._get_weather(city)
            
            if weather:
                self._city_label.config({'text': '{}, {}'.format(weather.get('city'), weather.get('country'))})
                self._coords_label.config({'text': weather.get('coords')})
                self._current_temp_label.config({'text': str(weather.get('c'))[:2] + '°C'})
                self._max_min_label.config({'text': str(weather.get('c_max'))[:2] + ' / ' + str(weather.get('c_min'))[:2]})
                self._weather_label.config({'text': weather.get('conditions') + ' (' + weather.get('description') + ')'})

                self._color_update(self._which_background(weather.get('hour')))
    
    def _get_weather(self, city):
        """
        Retrieve weather for given location using OpenWeatherMap API
        Weather data provided by OpenWeather, at openweathermap.org

        city: city name, string
        """
        info = None
        result = None
        
        try:
            # Request
            result = requests.get(self._url.format(city, self._api_key))

            # Process retrieved weather information
            if result:
                json = result.json()
                city = json['name']

                coords = self._degrees_to_dms(json['coord']['lat'], json['coord']['lon'])
                country = country_converter.convert(json['sys']['country'], to='name_short')

                k_temp = json['main']['temp']
                c_temp = k_temp-273.15
                f_temp = c_temp*1.8+32

                k_max = json['main']['temp_max']
                c_max = k_max-273.15
                f_max = c_max*1.8+32

                k_min = json['main']['temp_min']
                c_min = k_min-273.15
                f_min = c_min*1.8+32

                weather_condition = json['weather'][0]['main']
                weather_description = json['weather'][0]['description']

                timestamp = datetime.datetime.utcnow() + datetime.timedelta(0, int(json['timezone']))
                date = timestamp.strftime('%m/%d')
                hour = timestamp.hour
                minute = timestamp.minute
                
                info = {'city': city,
                        'country': country,
                        'coords': coords,
                        'c': c_temp,
                        'f': f_temp,
                        'c_max': c_max,
                        'f_max': f_max,
                        'c_min': c_min,
                        'f_min': f_min,
                        'conditions': weather_condition,
                        'description': weather_description,
                        'date': date,
                        'hour': hour,
                        'minute': minute}
            else:
                # Display error popup
                messagebox.showerror('Error', 'Cannot find "{}".'.format(city))
        except:
            # Display error popup
            messagebox.showerror('Error', 'Unable to retrieve weather data.')

        return info

if __name__ == '__main__':
    WeatherApp()