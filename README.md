# Thesis Data Collector

A small tool that records keyboard and mouse **timing/movement patterns** for a
Master's thesis on behavioral biometrics (Antalya Bilim University).

## Privacy

- The tool records **only timing and movement**, never the actual letters or words.
- Each key is replaced by an anonymous code, so the text you type **cannot be recovered**.
- Nothing is sent over the internet. Files are saved locally on your computer.
- **Do NOT type real passwords or personal information during the session.**

## Requirements

- Python 3.10+ ([python.org](https://www.python.org/downloads/), tick **"Add Python to PATH"** during install)
- One library: `pynput`

## Setup (once)

1. Download this repository: green **Code** button -> **Download ZIP**, then unzip.
   (Or: `git clone https://github.com/dastantolegenov/thesis-data-collector.git`)
2. Open a terminal **inside the unzipped folder**.
3. Install the library: pip install pynput

## Run the session

1. Start the tool: python collect_data.py
2. When asked for the ID, type the **participant ID given to you** (for example `P01`) and press Enter.
3. For **15 minutes**, use your computer **normally**: type your own text and use
   the mouse (browse, click, scroll). There is no right or wrong way.
4. **Do not type passwords or private information.**
5. To stop, press **ESC**.

## Send the files

- When you press ESC, the tool saves **2 files** in a folder called `data/raw/custom`
  (it also prints the exact location).
- The files are named `keystroke_<ID>.csv` and `mouse_<ID>.csv`.
- Please send **both files** to the researcher on **WhatsApp**.

Thank you for taking part!
