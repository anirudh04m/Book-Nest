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

interface Category {
  category_id: number;
  category_name: string;
  description: string;
}

interface Publisher {
  publisher_id: number;
  publisher_name: string;
  publisher_city: string;
}

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [publishers, setPublishers] = useState<Publisher[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    isbn: '',
    title: '',
    publication_year: new Date().getFullYear(),
    publisher_id: 1,
    category_id: 1,
    author_first_name: '',
    author_last_name: '',
    author_initials: '',
    author_role: 'Author',
    price: '',
    can_rent: false,
  });

  useEffect(() => {
    fetchBooks();
    fetchCategories();
    fetchPublishers();
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

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/py/categories');
      const data = await response.json();
      setCategories(data);
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, category_id: data[0].category_id }));
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchPublishers = async () => {
    try {
      const response = await fetch('/api/py/publishers');
      const data = await response.json();
      setPublishers(data);
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, publisher_id: data[0].publisher_id }));
      }
    } catch (error) {
      console.error('Error fetching publishers:', error);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const bookPayload = {
        ...formData,
        publication_year: typeof formData.publication_year === 'number' 
          ? formData.publication_year 
          : parseInt(formData.publication_year.toString()),
        publisher_id: typeof formData.publisher_id === 'number'
          ? formData.publisher_id
          : parseInt(formData.publisher_id.toString()),
        category_id: typeof formData.category_id === 'number'
          ? formData.category_id
          : parseInt(formData.category_id.toString()),
        price: formData.price ? parseFloat(formData.price.toString()) : null,
      };

      const response = await fetch('/api/py/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookPayload),
      });

      if (response.ok) {
        fetchBooks();
        setShowForm(false);
        setFormData({
          isbn: '',
          title: '',
          publication_year: new Date().getFullYear(),
          publisher_id: publishers.length > 0 ? publishers[0].publisher_id : 1,
          category_id: categories.length > 0 ? categories[0].category_id : 1,
          author_first_name: '',
          author_last_name: '',
          author_initials: '',
          author_role: 'Author',
          price: '',
          can_rent: false,
        });
        alert('Book created successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to create book'}`);
      }
    } catch (error) {
      console.error('Error creating book:', error);
      alert('Error creating book. Please try again.');
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
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Books</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            {showForm ? 'Cancel' : '+ Add Book'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-6 border border-gray-300 rounded-lg bg-gray-50">
          <h2 className="text-2xl font-semibold mb-4 text-gray-900">Add New Book</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ISBN *</label>
              <input
                type="text"
                value={formData.isbn}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Publication Year *</label>
              <input
                type="number"
                value={formData.publication_year}
                onChange={(e) => setFormData({ ...formData, publication_year: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Publisher *</label>
              <select
                value={formData.publisher_id}
                onChange={(e) => setFormData({ ...formData, publisher_id: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              >
                {publishers.map((publisher) => (
                  <option key={publisher.publisher_id} value={publisher.publisher_id}>
                    {publisher.publisher_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
              <select
                value={formData.category_id}
                onChange={(e) => setFormData({ ...formData, category_id: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              >
                {categories.map((category) => (
                  <option key={category.category_id} value={category.category_id}>
                    {category.category_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author First Name *</label>
              <input
                type="text"
                value={formData.author_first_name}
                onChange={(e) => setFormData({ ...formData, author_first_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author Last Name *</label>
              <input
                type="text"
                value={formData.author_last_name}
                onChange={(e) => setFormData({ ...formData, author_last_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author Initials</label>
              <input
                type="text"
                value={formData.author_initials}
                onChange={(e) => setFormData({ ...formData, author_initials: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                placeholder="Auto-generated if empty"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author Role</label>
              <select
                value={formData.author_role}
                onChange={(e) => setFormData({ ...formData, author_role: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
              >
                <option value="Author">Author</option>
                <option value="Co-Author">Co-Author</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Price (Optional)</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                placeholder="Leave empty to skip creating copy"
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.can_rent}
                onChange={(e) => setFormData({ ...formData, can_rent: e.target.checked })}
                className="mr-2"
              />
              <label className="text-sm font-medium text-gray-700">Can be rented</label>
            </div>
          </div>
          <button
            type="submit"
            className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create Book
          </button>
        </form>
      )}
      
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

