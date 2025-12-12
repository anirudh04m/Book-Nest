'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface BookDetail {
  isbn: string;
  title: string;
  author_name: string;
  category_name: string;
  publisher_name: string;
  publication_year: number;
  number_of_copies: number;
}

interface BookCopy {
  b_item_id: number;
  isbn: string;
  can_rent: number;
  price: number;
  description: string;
  status: string;
}

interface Review {
  review_id: number;
  content: string;
  reviewer: string;
  rating: number;
  review_date: string;
}

export default function BookDetailPage() {
  const params = useParams();
  const isbn = params.isbn as string;
  const [book, setBook] = useState<BookDetail | null>(null);
  const [copies, setCopies] = useState<BookCopy[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [showAddCopiesForm, setShowAddCopiesForm] = useState(false);
  const [reviewForm, setReviewForm] = useState({
    content: '',
    reviewer: '',
    rating: 5,
    item_id: null as number | null,
  });
  const [addCopiesForm, setAddCopiesForm] = useState({
    quantity: 1,
    price: '',
    can_rent: false,
  });

  useEffect(() => {
    if (isbn) {
      fetchBookDetails();
    }
  }, [isbn]);

  const fetchBookDetails = async () => {
    try {
      const [bookRes, copiesRes, itemsRes] = await Promise.all([
        fetch(`/api/py/books/${isbn}`),
        fetch(`/api/py/books/${isbn}/copies`),
        fetch('/api/py/items?item_type=Book'),
      ]);

      if (bookRes.ok) {
        const bookData = await bookRes.json();
        setBook(bookData);
      }

      const copiesData = await copiesRes.json();
      const itemsData = await itemsRes.json();

      // Merge copies with item details
      const copiesWithDetails = copiesData.map((copy: BookCopy) => {
        const item = itemsData.find((i: any) => i.item_id === copy.b_item_id);
        return {
          ...copy,
          price: item?.price || 0,
          description: item?.description || `Book Copy #${copy.b_item_id}`,
        };
      });

      setCopies(copiesWithDetails);

      // Get reviews for this book's items
      if (copiesWithDetails.length > 0) {
        const itemIds = copiesWithDetails.map((c: BookCopy) => c.b_item_id);
        const reviewsPromises = itemIds.map((itemId: number) =>
          fetch(`/api/py/reviews?item_id=${itemId}`).then((r) => r.json())
        );
        const reviewsArrays = await Promise.all(reviewsPromises);
        const allReviews = reviewsArrays.flat();
        setReviews(allReviews);
        if (copiesWithDetails.length > 0) {
          setReviewForm((prev) => ({ ...prev, item_id: copiesWithDetails[0].b_item_id }));
        }
      }
    } catch (error) {
      console.error('Error fetching book details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewForm.item_id) {
      alert('Please select a book copy');
      return;
    }

    try {
      const response = await fetch('/api/py/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: reviewForm.content,
          reviewer: reviewForm.reviewer,
          rating: reviewForm.rating,
          item_id: reviewForm.item_id,
        }),
      });

      if (response.ok) {
        alert('Review submitted successfully!');
        setShowReviewForm(false);
        setReviewForm({ content: '', reviewer: '', rating: 5, item_id: copies[0]?.b_item_id || null });
        fetchBookDetails();
      } else {
        const errorData = await response.json();
        alert(`Failed to submit review: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Error submitting review.');
    }
  };

  if (loading) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Loading...</div>;
  }

  if (!book) {
    return (
      <div className="p-8 bg-white min-h-screen text-gray-900">
        <Link href="/books" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Books
        </Link>
        <p>Book not found</p>
      </div>
    );
  }

  const availableCopies = copies.filter((c) => c.status === 'available');
  const averageRating =
    reviews.length > 0
      ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
      : 0;

  return (
    <div className="container mx-auto p-8 bg-white min-h-screen">
      <div className="mb-6">
        <Link href="/books" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Books
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{book.title}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Book Information */}
        <div className="lg:col-span-2">
          <div className="bg-white border border-gray-300 rounded-lg p-6 shadow-md mb-6">
            <div className="space-y-3">
              <div>
                <span className="font-semibold text-gray-700">ISBN:</span>
                <span className="ml-2 text-gray-900">{book.isbn}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Author:</span>
                <span className="ml-2 text-gray-900">{book.author_name}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Publisher:</span>
                <span className="ml-2 text-gray-900">{book.publisher_name}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Category:</span>
                <span className="ml-2 text-gray-900">{book.category_name}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Publication Year:</span>
                <span className="ml-2 text-gray-900">{book.publication_year}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Total Copies:</span>
                <span className="ml-2 text-gray-900">{book.number_of_copies}</span>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Available Copies:</span>
                <span className="ml-2 text-gray-900">{availableCopies.length}</span>
              </div>
              {averageRating > 0 && (
                <div>
                  <span className="font-semibold text-gray-700">Average Rating:</span>
                  <span className="ml-2 text-gray-900">
                    {averageRating.toFixed(1)} / 5.0 ({reviews.length} reviews)
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Available Copies */}
          <div className="bg-white border border-gray-300 rounded-lg p-6 shadow-md mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Available Copies ({availableCopies.length})</h2>
              <button
                onClick={() => setShowAddCopiesForm(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
              >
                + Add Copies
              </button>
            </div>
            
            {showAddCopiesForm && (
              <div className="mb-6 p-4 border-2 border-green-300 rounded-lg bg-green-50">
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Add Book Copies</h3>
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!addCopiesForm.price || parseFloat(addCopiesForm.price) <= 0) {
                      alert('Please enter a valid price');
                      return;
                    }
                    if (addCopiesForm.quantity <= 0) {
                      alert('Quantity must be greater than 0');
                      return;
                    }
                    
                    try {
                      const response = await fetch(`/api/py/inventory/${isbn}/add-copies?quantity=${addCopiesForm.quantity}&price=${parseFloat(addCopiesForm.price)}&can_rent=${addCopiesForm.can_rent}`, {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                        },
                      });
                      
                      if (response.ok) {
                        const result = await response.json();
                        alert(`Successfully added ${addCopiesForm.quantity} copy/copies!`);
                        setShowAddCopiesForm(false);
                        setAddCopiesForm({ quantity: 1, price: '', can_rent: false });
                        fetchBookDetails();
                      } else {
                        const error = await response.json();
                        alert(`Error: ${error.detail || 'Failed to add copies'}`);
                      }
                    } catch (error) {
                      console.error('Error adding copies:', error);
                      alert('Error adding copies. Please try again.');
                    }
                  }}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Quantity *</label>
                      <input
                        type="number"
                        min="1"
                        value={addCopiesForm.quantity}
                        onChange={(e) => setAddCopiesForm({ ...addCopiesForm, quantity: parseInt(e.target.value) || 1 })}
                        className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Price per Copy *</label>
                      <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        value={addCopiesForm.price}
                        onChange={(e) => setAddCopiesForm({ ...addCopiesForm, price: e.target.value })}
                        className="w-full h-10 px-4 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        placeholder="29.99"
                        required
                      />
                    </div>
                    <div className="flex items-end">
                      <label className="flex items-center p-3 border border-gray-300 rounded-lg bg-white cursor-pointer w-full h-10">
                        <input
                          type="checkbox"
                          checked={addCopiesForm.can_rent}
                          onChange={(e) => setAddCopiesForm({ ...addCopiesForm, can_rent: e.target.checked })}
                          className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                        />
                        <span className="text-sm font-medium text-gray-700">Can be rented</span>
                      </label>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                    >
                      Add Copies
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowAddCopiesForm(false);
                        setAddCopiesForm({ quantity: 1, price: '', can_rent: false });
                      }}
                      className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}
            
            {availableCopies.length > 0 ? (
              <div className="space-y-3">
                {availableCopies.map((copy) => (
                  <div
                    key={copy.b_item_id}
                    className="flex justify-between items-center p-3 border border-gray-200 rounded bg-gray-50"
                  >
                    <div>
                      <p className="font-medium text-gray-900">Copy #{copy.b_item_id}</p>
                      <p className="text-sm text-gray-600">
                        {copy.can_rent ? 'Can be rented' : 'Purchase only'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">${copy.price.toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600">No copies currently available</p>
              </div>
            )}
          </div>

          {/* Reviews */}
          <div className="bg-white border border-gray-300 rounded-lg p-6 shadow-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Reviews ({reviews.length})</h2>
              <button
                onClick={() => setShowReviewForm(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                + Add Review
              </button>
            </div>

            {reviews.length > 0 ? (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <div key={review.review_id} className="border-b border-gray-200 pb-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold text-gray-900">{review.reviewer}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(review.review_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center">
                        <span className="text-yellow-500 text-lg">★</span>
                        <span className="ml-1 text-gray-900">{review.rating}/5</span>
                      </div>
                    </div>
                    <p className="text-gray-700">{review.content}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">No reviews yet. Be the first to review!</p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 sticky top-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">Quick Actions</h3>
            <div className="space-y-3">
              <Link
                href="/orders/create"
                className="block w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-center"
              >
                Add to Order
              </Link>
              {availableCopies.some((c) => c.can_rent) && (
                <Link
                  href="/rentals"
                  className="block w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-center"
                >
                  Rent This Book
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Review Form Modal */}
      {showReviewForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <form
            onSubmit={handleSubmitReview}
            className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md"
          >
            <h2 className="text-2xl font-semibold mb-4 text-gray-900">Write a Review</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Your Name *</label>
                <input
                  type="text"
                  value={reviewForm.reviewer}
                  onChange={(e) => setReviewForm({ ...reviewForm, reviewer: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rating *</label>
                <select
                  value={reviewForm.rating}
                  onChange={(e) =>
                    setReviewForm({ ...reviewForm, rating: parseInt(e.target.value) })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                  required
                >
                  {[5, 4, 3, 2, 1].map((rating) => (
                    <option key={rating} value={rating}>
                      {rating} {rating === 1 ? 'star' : 'stars'}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Review *</label>
                <textarea
                  value={reviewForm.content}
                  onChange={(e) => setReviewForm({ ...reviewForm, content: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
                  rows={4}
                  required
                />
              </div>
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setShowReviewForm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Submit Review
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

