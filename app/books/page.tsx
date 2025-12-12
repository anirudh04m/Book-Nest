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
  const [showPublisherForm, setShowPublisherForm] = useState(false);
  const [newPublisher, setNewPublisher] = useState({ name: '', city: '' });
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

  const handleAddPublisher = async (e?: React.MouseEvent | React.KeyboardEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    if (!newPublisher.name.trim()) {
      alert('Please enter a publisher name');
      return;
    }
    
    try {
      const payload = {
        publisher_name: newPublisher.name.trim(),
        publisher_city: newPublisher.city.trim() || null,
      };
      
      console.log('Creating publisher with payload:', payload);
      
      const response = await fetch('/api/py/publishers', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (response.ok) {
        const createdPublisher = await response.json();
        console.log('Created publisher:', createdPublisher);
        
        if (createdPublisher && createdPublisher.publisher_id) {
          await fetchPublishers(); // Refresh publisher list
          setFormData(prev => ({ ...prev, publisher_id: createdPublisher.publisher_id }));
          setShowPublisherForm(false);
          setNewPublisher({ name: '', city: '' });
          alert(`Publisher "${createdPublisher.publisher_name}" added successfully!`);
        } else {
          alert('Publisher created but failed to get publisher ID');
        }
      } else {
        const errorText = await response.text();
        console.error('Error response text:', errorText);
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { detail: errorText || 'Unknown error' };
        }
        console.error('Error response:', errorData);
        alert(`Error: ${errorData.detail || 'Failed to add publisher'}`);
      }
    } catch (error) {
      console.error('Error adding publisher:', error);
      alert(`Error adding publisher: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
    
    // Validation
    if (!formData.isbn.trim()) {
      alert('Please enter an ISBN');
      return;
    }
    if (!formData.title.trim()) {
      alert('Please enter a title');
      return;
    }
    if (!formData.author_first_name.trim() || !formData.author_last_name.trim()) {
      alert('Please enter author first and last name');
      return;
    }
    if (publishers.length === 0) {
      alert('Please add at least one publisher first');
      return;
    }
    if (categories.length === 0) {
      alert('Categories are not available. Please initialize the database.');
      return;
    }
    
    try {
      const bookPayload = {
        ...formData,
        isbn: formData.isbn.trim(),
        title: formData.title.trim(),
        publication_year: typeof formData.publication_year === 'number' 
          ? formData.publication_year 
          : parseInt(formData.publication_year.toString()),
        publisher_id: typeof formData.publisher_id === 'number'
          ? formData.publisher_id
          : parseInt(formData.publisher_id.toString()),
        category_id: typeof formData.category_id === 'number'
          ? formData.category_id
          : parseInt(formData.category_id.toString()),
        author_first_name: formData.author_first_name.trim(),
        author_last_name: formData.author_last_name.trim(),
        author_initials: formData.author_initials.trim() || undefined,
        price: formData.price ? parseFloat(formData.price.toString()) : null,
      };

      const response = await fetch('/api/py/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookPayload),
      });

      if (response.ok) {
        const createdBook = await response.json();
        await fetchBooks();
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
        alert(`Book "${createdBook.title}" created successfully!`);
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Failed to create book'}`);
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
        <form 
          onSubmit={handleSubmit} 
          className="mb-6 p-6 border border-gray-300 rounded-lg bg-white shadow-md"
          onClick={(e) => {
            // Prevent form submission when clicking inside publisher form area
            const target = e.target as HTMLElement;
            if (target.closest('.publisher-form-container')) {
              e.stopPropagation();
            }
          }}
        >
          <h2 className="text-2xl font-semibold mb-6 text-gray-900">Add New Book</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">ISBN *</label>
              <input
                type="text"
                value={formData.isbn}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., 978-0-123456-78-9"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter book title"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Publication Year *</label>
              <input
                type="number"
                min="1000"
                max={new Date().getFullYear() + 1}
                value={formData.publication_year}
                onChange={(e) => setFormData({ ...formData, publication_year: parseInt(e.target.value) || new Date().getFullYear() })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Publisher *</label>
              <div className="flex gap-2 items-start">
                <select
                  value={formData.publisher_id}
                  onChange={(e) => setFormData({ ...formData, publisher_id: parseInt(e.target.value) })}
                  className="flex-1 h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                  disabled={publishers.length === 0}
                >
                  {publishers.length === 0 ? (
                    <option value="">No publishers available</option>
                  ) : (
                    publishers.map((publisher) => (
                      <option key={publisher.publisher_id} value={publisher.publisher_id}>
                        {publisher.publisher_name}
                      </option>
                    ))
                  )}
                </select>
                <button
                  type="button"
                  onClick={() => setShowPublisherForm(!showPublisherForm)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm whitespace-nowrap font-medium"
                  title="Add New Publisher"
                >
                  + Add New
                </button>
              </div>
              {showPublisherForm && (
                <div className="publisher-form-container mt-3 p-4 border-2 border-blue-300 rounded-lg bg-blue-50" onClick={(e) => e.stopPropagation()}>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Add New Publisher</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Publisher Name *</label>
                      <input
                        type="text"
                        placeholder="Enter publisher name"
                        value={newPublisher.name}
                        onChange={(e) => setNewPublisher({ ...newPublisher, name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddPublisher(e as any);
                          }
                        }}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">City (optional)</label>
                      <input
                        type="text"
                        placeholder="Enter city"
                        value={newPublisher.city}
                        onChange={(e) => setNewPublisher({ ...newPublisher, city: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddPublisher(e as any);
                          }
                        }}
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleAddPublisher}
                        className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                      >
                        Add Publisher
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowPublisherForm(false);
                          setNewPublisher({ name: '', city: '' });
                        }}
                        className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 text-sm font-medium"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
              <select
                value={formData.category_id}
                onChange={(e) => setFormData({ ...formData, category_id: parseInt(e.target.value) })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={categories.length === 0}
              >
                {categories.length === 0 ? (
                  <option value="">No categories available - please initialize database</option>
                ) : (
                  categories.map((category) => (
                    <option key={category.category_id} value={category.category_id}>
                      {category.category_name}
                    </option>
                  ))
                )}
              </select>
              {categories.length === 0 && (
                <p className="mt-1 text-xs text-red-600">
                  Categories are empty. Please trigger database initialization.
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Author First Name *</label>
              <input
                type="text"
                value={formData.author_first_name}
                onChange={(e) => setFormData({ ...formData, author_first_name: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter first name"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Author Last Name *</label>
              <input
                type="text"
                value={formData.author_last_name}
                onChange={(e) => setFormData({ ...formData, author_last_name: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter last name"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Author Initials (Optional)</label>
              <input
                type="text"
                value={formData.author_initials}
                onChange={(e) => setFormData({ ...formData, author_initials: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Auto-generated if empty"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Author Role</label>
              <select
                value={formData.author_role}
                onChange={(e) => setFormData({ ...formData, author_role: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Author">Author</option>
                <option value="Co-Author">Co-Author</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Price (Optional)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Leave empty to skip creating copy"
              />
              <p className="mt-1 text-xs text-gray-500">If price is provided, a book copy will be created</p>
            </div>
            <div className="flex items-center p-3 border border-gray-300 rounded-lg bg-gray-50">
              <input
                type="checkbox"
                id="can_rent"
                checked={formData.can_rent}
                onChange={(e) => setFormData({ ...formData, can_rent: e.target.checked })}
                className="mr-3 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="can_rent" className="text-sm font-medium text-gray-700 cursor-pointer">
                Can be rented (only applies if price is set)
              </label>
            </div>
          </div>
          <div className="mt-6 flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => {
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
              }}
              className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium shadow-md"
            >
              Create Book
            </button>
          </div>
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

