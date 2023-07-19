# TicketSage

This is a simple movie booking system built with Django. It allows users to view a list of movies, seats, and cinemas, create a new booking, and view the details of a booking.


**Features**:

- View a list of all movies
- View a list of all seats
- View the details of a cinema
- Create a new booking
- View the details of a booking
- Update movie data from TMDB API


**Installation**

1. Clone this repository:

```bash
git clone https://github.com/r3troseer/TicketSage.git
```

2. Navigate into the project directory:

```bash
cd TicketSage
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Run the migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

6. Open your web browser and navigate to `http://localhost:8000/`.


**Usage**

- To create a new booking, navigate to `/bookings/new/` and fill out the form with the seat row, seat number, movie selection, and cinema selection. Click the "Book" button to create the booking.

- To view the details of a booking, navigate to `/bookings/<booking_id>/`, replacing `<booking_id>` with the ID of the booking.

- To update movie data from an TMDB API, you can use the update_movie management command. Run the following command:

```bash
python manage.py update_movie
```
This command fetches the latest movie data from TMDB API and updates the movie table in the database with the new data.


**Contributing**

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
