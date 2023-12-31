# TicketSage

This is a simple movie booking system built with Django. It allows users to view a list of movies, seats, and cinemas, create a new booking, and view the details of a booking.

## Features:

- User authentication using dj-rest-auth
- Api view for list of available movies
- Api view for a showtime detail where booking is made
- Api view for detail of movie with list of showtimes
- API view for list of movies booked by authenticated user
- Update movie data from TMDB API
- Schedule showtimes for movies in the cinemas automatically

## Installation

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

## Usage

- To update movie data from TMDB API, you can use the update_movie management command. Run the following command:

```bash
python manage.py update_movies
```

This command fetches the latest movie data from TMDB API and updates the movie table in the database with the new data.

- To schedule showtimes for movies in the cinemas automatically, you can use the schedule_showtimes management command. Run the following command:

```bash
python manage.py schedule_showtimes

```

This command will schedule showtimes for movies in the cinemas between 8 am and 10 pm for the next 7 days. Showtimes are scheduled in a way that no two movies overlap, and movies are scheduled 1 hour after viewing ends to allow time for cleaning between screenings.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
