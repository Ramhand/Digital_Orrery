# Orrery Application

## Description
The **Orrery Application** is a Python-based visual representation of planetary data using real-time information from an API. The application displays the positions, altitudes, azimuths, and phases (for the Moon) of various planets and celestial objects in an interactive, rotating graphical user interface (GUI). 

This project leverages the Tkinter library for the GUI, while also integrating APIs to fetch live astronomical data.

## Features
- **Real-Time Planetary Data**: Uses an external API to retrieve real-time information about visible planets.
- **Interactive GUI**: Displays planets and their positions with smooth animations and interaction through a custom interface.
- **Location Configuration**: Allows the user to update location settings (latitude, longitude, elevation) for accurate results.
- **Celestial Movement Simulation**: Displays dynamic rotation of planets based on their positions, including rise and set times.

## Technologies Used
- **Python**: Core programming language.
- **Tkinter**: Used to create the graphical user interface.
- **Pandas**: Handles the planetary data.
- **Requests**: Used to interact with external APIs for planetary data.
- **Pillow (PIL)**: Image processing for rotating and displaying planet graphics.
- **BeautifulSoup**: Used to scrape rise and set times for celestial objects from an online source.

## Installation

To install and run the **Orrery Application**, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/orrery-app.git
    cd orrery-app
    ```

2. **Install Dependencies**:
   This project requires several Python packages, which you can install via pip:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    You can launch the GUI and start visualizing planetary data by running the `frontend.py` script:
    ```bash
    python src/frontend.py
    ```

## Usage

1. Upon launching, the application will display a rotating orrery of planets and celestial objects.
2. You can interact with the interface, and hover over planets to view their real-time altitude and azimuth data.
3. To update your location, right-click to open the **Location Settings** menu, input an address, and the application will adjust the planetary data based on your new coordinates.
4. The application will continue fetching and updating planetary data based on your location.

## API Usage
- **Visible Planets API**: Fetches live planetary data such as altitude, azimuth, and phase of celestial bodies. More info [here](https://api.visibleplanets.dev).
- **United States Naval Observatory**: Scrapes rise and set times of planets for accurate simulation.

## File Structure
orrery-app/
│
├── README.md              # Project overview and documentation
├── requirements.txt       # Python package requirements
├── src/                   # Source code files
│   ├── api_requests.py    # Handles API requests for planetary data
│   ├── planets.py         # Main logic for calculating planetary positions
│   └── frontend.py        # Tkinter GUI and display logic
├── GUI/                   # Graphics used in the application (planet images, arrows, etc.)
└── data/                  # Stores local data files like location or planetary position data

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- **Visible Planets API** for providing real-time planetary data.
- **United States Naval Observatory** for rise and set times.
- All contributors and collaborators for helping improve the project.

