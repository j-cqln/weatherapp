# Libraries
import os
import logging
import datetime
from configparser import ConfigParser

import requests
import country_converter

import tkinter as tk
from tkinter import font
from tkinter import messagebox

class WeatherApp:
    """
    Class for the weatherapp application

    Creates a GUI weather application
    """
    BUTTON_BACKGROUND_COLOR = '#ffffff'
    ENTRY_BACKGROUND_COLOR = '#ffffff'
    
    BUTTON_TEXT_COLOR = '#000000'
    ENTRY_TEXT_COLOR = '#000000'
    PROMPT_TEXT_COLOR = '#959595'
    
    LIGHT_DISPLAY_TEXT_COLOR = '#000000'
    DARK_DISPLAY_TEXT_COLOR = '#ffffff'

    DAY_IMAGE_FILE = 'day.png'
    SUNRISE_IMAGE_FILE = 'sunrise.png'
    SUNSET_IMAGE_FILE = 'sunset.png'
    NIGHT_IMAGE_FILE = 'night.png'

    def __init__(self):
        """
        Initializes the WeatherApp class
        """
        self._file_location = os.path.dirname('__file__')
        self._resources_path = os.path.join(self._file_location, 'resources/')

        # Parse configuration file
        self._config_file = os.path.join(self._resources_path, 'config.ini')

        self._config = ConfigParser()
        self._config.read(self._config_file)
        self._api_key = self._config['Default']['api']

        # OpenWeatherMap URL
        self._url = 'http://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}'

        # GUI
        self._root = tk.Tk()
        self._root.title('weatherapp')
        self._root.geometry('300x400')
        self._root.minsize(300, 400)
        self._root.maxsize(300, 400)

        # Font
        self._root.option_add('*Font', 'helvetica')
        self._default_font = tk.font.Font(family='helvetica', size=10)
        self._entry_font = tk.font.Font(family='helvetica', size=9)
        self._button_font = tk.font.Font(family='helvetica', size=9)
        self._location_font = tk.font.Font(family='helvetica', size=12)
        self._coords_font = tk.font.Font(family='helvetica', size=9)
        self._time_font = tk.font.Font(family='helvetica', size=9)
        self._current_temp_font = tk.font.Font(family='helvetica', size=16)
        self._max_min_font = tk.font.Font(family='helvetica', size=9)

        # Create canvas
        self._canvas = tk.Canvas(self._root, width=300, height=400, borderwidth=0, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky='NWSE')

        # Create background
        self._background = self._canvas.create_image(0, 0, anchor='nw')

        # Weather information
        self._weather = {}
        
        # For location entry
        self._city_prompt = ' city here...'
        self._country_prompt = ' country here...'
        
        self._city_text = tk.StringVar(self._root)
        self._city_entry = tk.Entry(self._root, textvariable=self._city_text, font=self._entry_font, width=17, justify='left', borderwidth=0, highlightthickness=0)
        self._city_entry.insert(0, self._city_prompt)
        self._city_entry.bind('<FocusIn>', lambda event: self._entry_focus(self._city_entry))
        self._city_entry.bind('<FocusOut>', lambda event: self._entry_unfocus(self._city_entry))
        self._city_entry_window = self._canvas.create_window(9, 10, anchor='nw', window=self._city_entry)

        self._country_text = tk.StringVar(self._root)
        self._country_entry = tk.Entry(self._root, textvariable=self._country_text, font=self._entry_font, width=17, justify='left', borderwidth=0, highlightthickness=0)
        self._country_entry.insert(0, self._country_prompt)
        self._country_entry.bind('<FocusIn>', lambda event: self._entry_focus(self._country_entry))
        self._country_entry.bind('<FocusOut>', lambda event: self._entry_unfocus(self._country_entry))
        self._country_entry_window = self._canvas.create_window(139, 10, anchor='nw', window=self._country_entry)

        # Search button
        self._search_button = tk.Label(self._root, text='  >', font=self._button_font, width=3, anchor='nw', borderwidth=0, highlightthickness=0)
        self._search_button.bind('<Button-1>', self._add_new_location)
        self._search_button_window = self._canvas.create_window(269, 10, anchor='nw', window=self._search_button)

        # Temperature degrees display mode
        self._degrees_mode = {'mode': 'celsius', 'symbol': '°C', 'key': 'c'}
        self._degrees_mode_button = tk.Label(self._root, text=' mode: ' + self._degrees_mode['symbol'] + ' ', font=self._button_font, anchor='nw', borderwidth=0, highlightthickness=0)
        self._degrees_mode_button.bind('<Button-1>', self._toggle_degrees_mode)
        self._degrees_mode_button_window = self._canvas.create_window(9, 370, anchor='nw', window=self._degrees_mode_button)

        # Location information
        self._canvas_text_dictionary = {}
        
        self._location_text = self._canvas.create_text(9, 36, text='', font=self._location_font, anchor='nw')
        self._coords_text = self._canvas.create_text(9, 61, text='', font=self._coords_font, anchor='nw')
        self._time_text = self._canvas.create_text(9, 83, text='', font=self._time_font, anchor='nw')
        self._current_temp_text = self._canvas.create_text(8, 103, text='', font=self._current_temp_font, anchor='nw')
        self._max_min_text = self._canvas.create_text(60, 110, text='', font=self._max_min_font, anchor='nw')
        self._weather_text = self._canvas.create_text(9, 131, text='', font=self._default_font, anchor='nw')
        
        self._canvas_text_dictionary.update({'location': self._location_text, 'coords': self._coords_text, 'time': self._time_text, 'current_temp': self._current_temp_text, 'max_min': self._max_min_text, 'weather': self._weather_text})
        
        # Determine theme based on current time
        now = datetime.datetime.now()
        self._update_theme(now.hour, now.minute)
        
        # Allow all widgets to be focusable on left click
        self._root.bind_all('<Button-1>', lambda event: event.widget.focus_set())

        # Application loop
        self._root.mainloop()
    
    def _entry_focus(self, widget):
        """
        Focuses on the given entry widget, remove prompt text if it is displayed

        widget: Entry widget to focus on, tkinter widget
        """
        if widget == self._city_entry:
            prompt_text = self._city_prompt
        elif widget == self._country_entry:
            prompt_text = self._country_prompt
        
        if widget.get() == prompt_text:
            widget.delete(1, tk.END)
            
        widget.config({'foreground': WeatherApp.ENTRY_TEXT_COLOR})

    def _entry_unfocus(self, widget):
        """
        Unfocuses from the given entry widget, restoring prompt text if no text entered

        widget: Entry widget to unfocus from, tkinter widget
        """
        if widget == self._city_entry:
            prompt_text = self._city_prompt
        elif widget == self._country_entry:
            prompt_text = self._country_prompt
        
        if widget.get() == '' or widget.get() == ' ':
            widget.delete(0, tk.END)
            widget.insert(0, prompt_text)

        widget.config({'foreground': WeatherApp.PROMPT_TEXT_COLOR})
        self._root.focus_set()
    
    def _update_theme(self, hour, minute):
        """
        Updates text color and background image based on given time

        hour: hour, int
        minute: minute, int
        """
        # Background and text color based on given time
        time = hour * 60 + minute
        
        if time < 300 or time > 1200:
            self._text_color = WeatherApp.DARK_DISPLAY_TEXT_COLOR
            self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, WeatherApp.NIGHT_IMAGE_FILE))
        elif time > 479 and time < 1020:
            self._text_color = WeatherApp.LIGHT_DISPLAY_TEXT_COLOR
            self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, WeatherApp.DAY_IMAGE_FILE))
        elif time > 300 and time < 480:
            self._text_color = WeatherApp.DARK_DISPLAY_TEXT_COLOR
            self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, WeatherApp.SUNRISE_IMAGE_FILE))
        else:
            self._text_color = WeatherApp.DARK_DISPLAY_TEXT_COLOR
            self._background_image = tk.PhotoImage(file=os.path.join(self._resources_path, WeatherApp.SUNSET_IMAGE_FILE))

        self._canvas.itemconfigure(self._background, image=self._background_image)

        for key, value in self._canvas_text_dictionary.items():
            self._canvas.itemconfig(value, fill=self._text_color)
        
        # Widget background and text color
        self._city_entry.config({'foreground': WeatherApp.PROMPT_TEXT_COLOR})
        self._city_entry.config({'background': WeatherApp.ENTRY_BACKGROUND_COLOR})

        self._country_entry.config({'foreground': WeatherApp.PROMPT_TEXT_COLOR})
        self._country_entry.config({'background': WeatherApp.ENTRY_BACKGROUND_COLOR})
        
        self._search_button.config({'foreground': WeatherApp.BUTTON_TEXT_COLOR})
        self._search_button.config({'background': WeatherApp.BUTTON_BACKGROUND_COLOR})

        self._degrees_mode_button.config({'foreground': WeatherApp.BUTTON_TEXT_COLOR})
        self._degrees_mode_button.config({'background': WeatherApp.BUTTON_BACKGROUND_COLOR})

    def _toggle_degrees_mode(self, *args):
        """
        Toggles the scale, either Celsius or Fahrenheit, used for temperature
        """
        # Toggle between Celsius and Fahrenheit
        if self._degrees_mode['mode'] == 'celsius':
            self._degrees_mode = {'mode': 'fahrenheit', 'symbol': '°F', 'key': 'f'}
        else:
            self._degrees_mode = {'mode': 'celsius', 'symbol': '°C', 'key': 'c'}

        self._degrees_mode_button.config({'text': ' mode: ' + self._degrees_mode['symbol'] + ' '})

        # Update displayed weather information
        self._display_weather()

    def _degrees_to_dms(self, lat, lon):
        """
        Converts latitude and longitude in decimal degrees to degrees, minutes, seconds

        lat: latitude, float
        lon: longitude, float

        return: formatted latitude and longitude, string
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
            return

    def _add_new_location(self, *args):
        """
        Adds new location to weather application
        """
        # Retrieve user-entered location
        city = self._city_text.get().strip()
        country = self._country_text.get().strip()

        country_converter.convert(country, to='ISO2')
        
        if country[:2] != country:
            country = ''

        # If not placeholder text, retrieve weather information
        if city != self._city_prompt.strip():
            weather = self._get_weather(city, country)

            # Display weather information
            if weather:
                self._weather = weather
                self._display_weather()
    
    def _get_weather(self, city, country):
        """
        Retrieves weather for given location using OpenWeatherMap API
        Weather data provided by OpenWeather, at openweathermap.org

        city: city name, string
        country: country name, string

        return: weather information for the given location, dictionary
        """
        info = None
        result = None
        
        try:
            # Request
            result = requests.get(self._url.format(city, country, self._api_key))

            # Process retrieved weather information
            if result:
                json = result.json()
                city = json['name']

                coords = self._degrees_to_dms(json['coord']['lat'], json['coord']['lon'])
                country = country_converter.convert(json['sys']['country'], to='name_short')

                k_temp = json['main']['temp']
                c_temp = k_temp - 273.15
                f_temp = c_temp * 1.8 + 32

                k_max = json['main']['temp_max']
                c_max = k_max - 273.15
                f_max = c_max * 1.8 + 32

                k_min = json['main']['temp_min']
                c_min = k_min - 273.15
                f_min = c_min * 1.8 + 32

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

    def _display_weather(self):
        """
        Displays weather information
        """
        if self._weather:
            self._canvas.itemconfigure(self._canvas_text_dictionary['location'], text='{}, {}'.format(self._weather.get('city'), self._weather.get('country')))
            self._canvas.itemconfigure(self._canvas_text_dictionary['coords'], text=self._weather.get('coords'))
            self._canvas.itemconfigure(self._canvas_text_dictionary['time'], text='{:02d}:{:02d}'.format(int(self._weather.get('hour')), int(self._weather.get('minute'))))
            self._canvas.itemconfigure(self._canvas_text_dictionary['current_temp'], text='{:d}{}'.format(int(self._weather.get(self._degrees_mode['key'])), self._degrees_mode['symbol']))
            self._canvas.itemconfigure(self._canvas_text_dictionary['max_min'], text='{:d} / {:d}'.format(int(self._weather.get(self._degrees_mode['key'] + '_max')), int(self._weather.get(self._degrees_mode['key'] + '_min'))))
            self._canvas.itemconfigure(self._canvas_text_dictionary['weather'], text='{} ({})'.format(self._weather.get('conditions'), self._weather.get('description')))

            # Position temperature text
            length = len(str(int(self._weather.get(self._degrees_mode['key']))))
            x = (length - 2) * 10
            
            self._canvas.moveto(self._canvas_text_dictionary['max_min'], 60, 110)
            self._canvas.move(self._canvas_text_dictionary['max_min'], x, 0)
            
            self._update_theme(self._weather.get('hour'), self._weather.get('minute'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    WeatherApp()