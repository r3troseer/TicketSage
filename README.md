# TicketSage

This is a simple movie booking system built with Django. It allows users to view a list of movies, seats, and cinemas, create a new booking, and view the details of a booking.

**Features**:

- View a list of all movies
- View a list of all seats
- View the details of a cinema
- Create a new booking
- View the details of a booking

**Installation**

1. Clone this repository:
```
git clone https://github.com/r3troseer/TicketSage.git
```
2. Navigate into the project directory:
```
cd TicketSage
```
3. Install the required dependencies:
```
pip install -r requirements.txt
```
4. Run the migrations:
```
python manage.py migrate
```
5. Start the development server:
```
python manage.py runserver
```
6. Open your web browser and navigate to `http://localhost:8000/`.

**Usage**
- To create a new booking, navigate to `/bookings/new/` and fill out the form with the seat row, seat number, movie selection, and cinema selection. Click the "Book" button to create the booking.

- To view the details of a booking, navigate to `/bookings/<booking_id>/`, replacing `<booking_id>` with the ID of the booking.

**Contributing**

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


