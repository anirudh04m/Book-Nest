'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Customer {
  customer_id: number;
  first_name: string;
  last_name: string;
  customer_type: string;
}

interface Item {
  item_id: number;
  description: string;
  price: number;
  item_type: string;
}

interface BookForOrder {
  isbn: string;
  title: string;
  author_name: string;
  available_copies: number;
  price: number;
}

interface Promotion {
  promotion_id: number;
  code: string;
  discount_percent: number;
  description: string;
}

export default function CreateOrderPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [books, setBooks] = useState<BookForOrder[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<number | null>(null);
  const [selectedBooks, setSelectedBooks] = useState<Map<string, number>>(new Map()); // isbn -> quantity
  const [selectedItems, setSelectedItems] = useState<Map<number, number>>(new Map()); // item_id -> quantity
  const [selectedPromotion, setSelectedPromotion] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [customersRes, booksRes, itemsRes, promotionsRes] = await Promise.all([
        fetch('/api/py/customers'),
        fetch('/api/py/books/for-ordering'),
        fetch('/api/py/items?item_type=Merchandise'),
        fetch('/api/py/promotions'),
      ]);

      const customersData = await customersRes.json();
      const booksData = await booksRes.json();
      const itemsData = await itemsRes.json();
      const promotionsData = await promotionsRes.json();

      setCustomers(customersData);
      setBooks(booksData);
      setItems(itemsData);
      setPromotions(promotionsData);
      if (customersData.length > 0) {
        setSelectedCustomer(customersData[0].customer_id);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const addBook = (isbn: string) => {
    setSelectedBooks((prev) => {
      const newMap = new Map(prev);
      const book = books.find(b => b.isbn === isbn);
      const currentQty = newMap.get(isbn) || 0;
      if (book && currentQty < book.available_copies) {
        newMap.set(isbn, currentQty + 1);
      }
      return newMap;
    });
  };

  const removeBook = (isbn: string) => {
    setSelectedBooks((prev) => {
      const newMap = new Map(prev);
      const currentQty = newMap.get(isbn) || 0;
      if (currentQty <= 1) {
        newMap.delete(isbn);
      } else {
        newMap.set(isbn, currentQty - 1);
      }
      return newMap;
    });
  };

  const addItem = (itemId: number) => {
    setSelectedItems((prev) => {
      const newMap = new Map(prev);
      newMap.set(itemId, (newMap.get(itemId) || 0) + 1);
      return newMap;
    });
  };

  const removeItem = (itemId: number) => {
    setSelectedItems((prev) => {
      const newMap = new Map(prev);
      const currentQty = newMap.get(itemId) || 0;
      if (currentQty <= 1) {
        newMap.delete(itemId);
      } else {
        newMap.set(itemId, currentQty - 1);
      }
      return newMap;
    });
  };

  const calculateTotal = () => {
    let total = 0;
    
    // Add book totals
    selectedBooks.forEach((quantity, isbn) => {
      const book = books.find((b) => b.isbn === isbn);
      if (book) {
        total += book.price * quantity;
      }
    });
    
    // Add item totals
    selectedItems.forEach((quantity, itemId) => {
      const item = items.find((i) => i.item_id === itemId);
      if (item) {
        total += item.price * quantity;
      }
    });

    if (selectedPromotion) {
      const promotion = promotions.find((p) => p.promotion_id === selectedPromotion);
      if (promotion) {
        total = total * (1 - promotion.discount_percent / 100);
      }
    }

    return total;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomer || (selectedBooks.size === 0 && selectedItems.size === 0)) {
      alert('Please select a customer and at least one item');
      return;
    }

    setSubmitting(true);
    try {
      // Build items array with ISBN for books and item_id for other items
      const orderItems: Array<{isbn?: string; item_id?: number; quantity: number}> = [];
      
      // Add books
      selectedBooks.forEach((quantity, isbn) => {
        orderItems.push({ isbn, quantity });
      });
      
      // Add other items
      selectedItems.forEach((quantity, itemId) => {
        orderItems.push({ item_id: itemId, quantity });
      });

      const response = await fetch('/api/py/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: selectedCustomer,
          promotion_id: selectedPromotion,
          items: orderItems,
        }),
      });

      if (response.ok) {
        alert('Order created successfully!');
        // Reset form
        setSelectedBooks(new Map());
        setSelectedItems(new Map());
        setSelectedPromotion(null);
        window.location.href = '/orders';
      } else {
        const errorData = await response.json();
        alert(`Failed to create order: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error creating order:', error);
      alert('Error creating order.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Loading...</div>;
  }

  const selectedBooksList = Array.from(selectedBooks.entries())
    .map(([isbn, quantity]) => {
      const book = books.find((b) => b.isbn === isbn);
      return book ? { ...book, quantity, type: 'book' } : null;
    })
    .filter((item) => item !== null) as (BookForOrder & { quantity: number; type: string })[];

  const selectedItemsList = Array.from(selectedItems.entries())
    .map(([itemId, quantity]) => {
      const item = items.find((i) => i.item_id === itemId);
      return item ? { ...item, quantity, type: 'item' } : null;
    })
    .filter((item) => item !== null) as (Item & { quantity: number; type: string })[];

  return (
    <div className="container mx-auto p-8 bg-white min-h-screen">
      <div className="mb-6">
        <Link href="/orders" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Orders
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Create New Order</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer Selection */}
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-300">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Customer *
          </label>
          <select
            value={selectedCustomer || ''}
            onChange={(e) => setSelectedCustomer(parseInt(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
            required
          >
            <option value="">Select a customer</option>
            {customers.map((customer) => (
              <option key={customer.customer_id} value={customer.customer_id}>
                {customer.first_name} {customer.last_name} ({customer.customer_type})
              </option>
            ))}
          </select>
        </div>

        {/* Books Selection */}
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-300">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">Select Books</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
            {books.map((book) => {
              const selectedQty = selectedBooks.get(book.isbn) || 0;
              const canAddMore = selectedQty < book.available_copies;
              return (
                <div
                  key={book.isbn}
                  className="flex items-center justify-between p-3 border border-gray-300 rounded bg-white"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{book.title}</p>
                    <p className="text-sm text-gray-600">{book.author_name}</p>
                    <p className="text-sm text-gray-600">
                      ${book.price.toFixed(2)} • {book.available_copies} available
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => removeBook(book.isbn)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                      disabled={selectedQty === 0}
                    >
                      -
                    </button>
                    <span className="w-8 text-center text-gray-900">
                      {selectedQty}
                    </span>
                    <button
                      type="button"
                      onClick={() => addBook(book.isbn)}
                      className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                      disabled={!canAddMore}
                      title={!canAddMore ? 'No more copies available' : ''}
                    >
                      +
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Other Items Selection */}
        {items.length > 0 && (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-300">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Select Other Items</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
              {items.map((item) => (
                <div
                  key={item.item_id}
                  className="flex items-center justify-between p-3 border border-gray-300 rounded bg-white"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.description}</p>
                    <p className="text-sm text-gray-600">${item.price.toFixed(2)} - {item.item_type}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => removeItem(item.item_id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                      disabled={!selectedItems.has(item.item_id)}
                    >
                      -
                    </button>
                    <span className="w-8 text-center text-gray-900">
                      {selectedItems.get(item.item_id) || 0}
                    </span>
                    <button
                      type="button"
                      onClick={() => addItem(item.item_id)}
                      className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Selected Items Summary */}
        {(selectedBooksList.length > 0 || selectedItemsList.length > 0) && (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-300">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Order Summary</h2>
            <ul className="space-y-2 mb-4">
              {selectedBooksList.map((book) => (
                <li key={book.isbn} className="flex justify-between text-gray-700">
                  <span>
                    {book.title} x {book.quantity}
                  </span>
                  <span>${(book.price * book.quantity).toFixed(2)}</span>
                </li>
              ))}
              {selectedItemsList.map((item) => (
                <li key={item.item_id} className="flex justify-between text-gray-700">
                  <span>
                    {item.description} x {item.quantity}
                  </span>
                  <span>${(item.price * item.quantity).toFixed(2)}</span>
                </li>
              ))}
            </ul>

            {/* Promotion Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Promotion (Optional)
              </label>
              <select
                value={selectedPromotion || ''}
                onChange={(e) =>
                  setSelectedPromotion(e.target.value ? parseInt(e.target.value) : null)
                }
                className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
              >
                <option value="">No promotion</option>
                {promotions.map((promotion) => (
                  <option key={promotion.promotion_id} value={promotion.promotion_id}>
                    {promotion.code} - {promotion.discount_percent}% off ({promotion.description})
                  </option>
                ))}
              </select>
            </div>

            <div className="border-t border-gray-300 pt-4">
              <div className="flex justify-between items-center">
                <span className="text-xl font-semibold text-gray-900">Total:</span>
                <span className="text-2xl font-bold text-gray-900">${calculateTotal().toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={submitting || (selectedBooks.size === 0 && selectedItems.size === 0)}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {submitting ? 'Creating Order...' : 'Create Order'}
        </button>
      </form>
    </div>
  );
}

