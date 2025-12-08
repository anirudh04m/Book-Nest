'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Book {
  isbn: string;
  title: string;
  author_name: string;
  category_name: string;
  publisher_name: string;
  publication_year: number;
  number_of_copies: number;
}

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await fetch('/api/py/books');
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error('Error fetching books:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm) {
      fetchBooks();
      return;
    }
    try {
      const response = await fetch(`/api/py/books/search/${encodeURIComponent(searchTerm)}`);
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error('Error searching books:', error);
    }
  };

  if (loading) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Loading...</div>;
  }

  return (
    <div className="container mx-auto p-8 bg-white min-h-screen">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Home
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Books</h1>
      </div>
      
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Search books..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-500"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {books.map((book) => (
          <div key={book.isbn} className="border border-gray-300 rounded-lg p-6 shadow-md hover:shadow-lg transition bg-white">
            <h2 className="text-xl font-semibold mb-2 text-gray-900">{book.title}</h2>
            <p className="text-gray-600 mb-1">Author: {book.author_name}</p>
            <p className="text-gray-600 mb-1">Category: {book.category_name}</p>
            <p className="text-gray-600 mb-1">Publisher: {book.publisher_name}</p>
            <p className="text-gray-600 mb-1">Year: {book.publication_year}</p>
            <p className="text-gray-600 mb-4">Copies: {book.number_of_copies}</p>
            <Link
              href={`/books/${book.isbn}`}
              className="text-blue-600 hover:underline"
            >
              View Details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

