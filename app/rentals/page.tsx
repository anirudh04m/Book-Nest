'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface BookRent {
  book_rent_id: number;
  customer_id: number;
  b_item_id: number;
  rent_date: string;
  return_date: string | null;
  penalty: number | null;
  book_title?: string;
  customer_name?: string;
}

interface Customer {
  customer_id: number;
  first_name: string;
  last_name: string;
}

interface BookForRent {
  isbn: string;
  title: string;
  author_name: string;
  available_copies: number;
}

export default function RentalsPage() {
  const [rentals, setRentals] = useState<BookRent[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [availableBooks, setAvailableBooks] = useState<BookForRent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRentForm, setShowRentForm] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<number | null>(null);
  const [selectedIsbn, setSelectedIsbn] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [rentalsRes, customersRes, booksRes] = await Promise.all([
        fetch('/api/py/book-rents'),
        fetch('/api/py/customers'),
        fetch('/api/py/books/for-renting'),
      ]);

      const rentalsData = await rentalsRes.json();
      const customersData = await customersRes.json();
      const booksData = await booksRes.json();

      // Rentals already have book_title and customer_name from the API
      setRentals(rentalsData);
      setCustomers(customersData);
      setAvailableBooks(booksData);
      
      if (customersData.length > 0) {
        setSelectedCustomer(customersData[0].customer_id);
      }
      if (booksData.length > 0) {
        setSelectedIsbn(booksData[0].isbn);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRent = async () => {
    if (!selectedCustomer || !selectedIsbn) {
      alert('Please select a customer and a book');
      return;
    }

    try {
      const response = await fetch('/api/py/book-rents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: selectedCustomer,
          isbn: selectedIsbn,
        }),
      });

      if (response.ok) {
        alert('Book rented successfully!');
        setShowRentForm(false);
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`Failed to rent book: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error renting book:', error);
      alert('Error renting book.');
    }
  };

  const handleReturn = async (rentId: number) => {
    if (!confirm('Mark this book as returned?')) {
      return;
    }

    try {
      const response = await fetch(`/api/py/book-rents/${rentId}/return`, {
        method: 'PUT',
      });

      if (response.ok) {
        alert('Book returned successfully!');
        fetchData();
      } else {
        const errorData = await response.json();
        alert(`Failed to return book: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error returning book:', error);
      alert('Error returning book.');
    }
  };

  if (loading) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Loading...</div>;
  }

  const activeRentals = rentals.filter((r) => !r.return_date);
  const returnedRentals = rentals.filter((r) => r.return_date);

  return (
    <div className="container mx-auto p-8 bg-white min-h-screen">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Home
        </Link>
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Book Rentals</h1>
          <button
            onClick={() => setShowRentForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + Rent Book
          </button>
        </div>
      </div>

      {/* Rent Form Modal */}
      {showRentForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
            <h2 className="text-2xl font-semibold mb-4 text-gray-900">Rent a Book</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Customer *</label>
                <select
                  value={selectedCustomer || ''}
                  onChange={(e) => setSelectedCustomer(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                  required
                >
                  {customers.map((customer) => (
                    <option key={customer.customer_id} value={customer.customer_id}>
                      {customer.first_name} {customer.last_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Book *</label>
                <select
                  value={selectedIsbn || ''}
                  onChange={(e) => setSelectedIsbn(e.target.value)}
                  className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select a book</option>
                  {availableBooks.map((book) => (
                    <option key={book.isbn} value={book.isbn}>
                      {book.title} by {book.author_name} ({book.available_copies} available)
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setShowRentForm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={handleRent}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Rent Book
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active Rentals */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-900">Active Rentals ({activeRentals.length})</h2>
        {activeRentals.length > 0 ? (
          <div className="space-y-4">
            {activeRentals.map((rental) => (
              <div
                key={rental.book_rent_id}
                className="border border-gray-300 rounded-lg p-6 shadow-md bg-white"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {rental.book_title || `Book #${rental.b_item_id}`}
                    </h3>
                    <p className="text-gray-600">ISBN: {rental.isbn || 'N/A'}</p>
                    <p className="text-gray-600">Customer: {rental.customer_name || `Customer #${rental.customer_id}`}</p>
                    <p className="text-gray-600">
                      Rented: {new Date(rental.rent_date).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleReturn(rental.book_rent_id)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Return Book
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No active rentals</p>
        )}
      </div>

      {/* Returned Rentals */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-900">Returned Rentals ({returnedRentals.length})</h2>
        {returnedRentals.length > 0 ? (
          <div className="space-y-4">
            {returnedRentals.map((rental) => (
              <div
                key={rental.book_rent_id}
                className="border border-gray-300 rounded-lg p-6 shadow-md bg-gray-50"
              >
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {rental.book_title || `Book #${rental.b_item_id}`}
                  </h3>
                  <p className="text-gray-600">ISBN: {rental.isbn || 'N/A'}</p>
                  <p className="text-gray-600">Customer: {rental.customer_name || `Customer #${rental.customer_id}`}</p>
                  <p className="text-gray-600">
                    Rented: {new Date(rental.rent_date).toLocaleDateString()}
                  </p>
                  <p className="text-gray-600">
                    Returned: {rental.return_date ? new Date(rental.return_date).toLocaleDateString() : 'N/A'}
                  </p>
                  {rental.penalty && rental.penalty > 0 && (
                    <p className="text-red-600 font-semibold">Penalty: ${rental.penalty.toFixed(2)}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No returned rentals</p>
        )}
      </div>
    </div>
  );
}

