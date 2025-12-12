'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface DashboardStats {
  total_books: number;
  total_customers: number;
  total_orders: number;
  total_revenue: number;
  active_rentals: number;
  total_reviews: number;
}

interface PopularBook {
  isbn: string;
  title: string;
  rental_count: number;
}

interface RecentOrder {
  order_id: number;
  order_amount: number;
  order_date: string;
  customer_name: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [popularBooks, setPopularBooks] = useState<PopularBook[]>([]);
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, popularRes, ordersRes] = await Promise.all([
        fetch('/api/py/statistics/dashboard'),
        fetch('/api/py/statistics/popular-books?limit=5'),
        fetch('/api/py/statistics/recent-orders?limit=5'),
      ]);

      const statsData = await statsRes.json();
      const popularData = await popularRes.json();
      const ordersData = await ordersRes.json();

      setStats(statsData);
      setPopularBooks(popularData);
      setRecentOrders(ordersData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Loading...</div>;
  }

  if (!stats) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Error loading dashboard</div>;
  }

  return (
    <div className="container mx-auto p-8 bg-white min-h-screen">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Home
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-blue-600 mb-2">Total Books</h3>
          <p className="text-3xl font-bold text-blue-900">{stats.total_books}</p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-green-600 mb-2">Total Customers</h3>
          <p className="text-3xl font-bold text-green-900">{stats.total_customers}</p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-purple-600 mb-2">Total Orders</h3>
          <p className="text-3xl font-bold text-purple-900">{stats.total_orders}</p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-yellow-600 mb-2">Total Revenue</h3>
          <p className="text-3xl font-bold text-yellow-900">${stats.total_revenue.toFixed(2)}</p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-orange-600 mb-2">Active Rentals</h3>
          <p className="text-3xl font-bold text-orange-900">{stats.active_rentals}</p>
        </div>

        <div className="bg-pink-50 border border-pink-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-pink-600 mb-2">Total Reviews</h3>
          <p className="text-3xl font-bold text-pink-900">{stats.total_reviews}</p>
        </div>
      </div>

      {/* Popular Books and Recent Orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Popular Books */}
        <div className="bg-white border border-gray-300 rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Most Popular Books</h2>
          {popularBooks.length > 0 ? (
            <ul className="space-y-3">
              {popularBooks.map((book) => (
                <li key={book.isbn} className="flex justify-between items-center border-b border-gray-200 pb-2">
                  <div>
                    <Link href={`/books/${book.isbn}`} className="text-blue-600 hover:underline font-medium">
                      {book.title}
                    </Link>
                    <p className="text-sm text-gray-600">ISBN: {book.isbn}</p>
                  </div>
                  <span className="text-gray-700 font-semibold">{book.rental_count} rentals</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600">No rental data available</p>
          )}
        </div>

        {/* Recent Orders */}
        <div className="bg-white border border-gray-300 rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Recent Orders</h2>
          {recentOrders.length > 0 ? (
            <ul className="space-y-3">
              {recentOrders.map((order) => (
                <li key={order.order_id} className="flex justify-between items-center border-b border-gray-200 pb-2">
                  <div>
                    <Link href={`/orders`} className="text-blue-600 hover:underline font-medium">
                      Order #{order.order_id}
                    </Link>
                    <p className="text-sm text-gray-600">{order.customer_name}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(order.order_date).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="text-gray-900 font-bold">${order.order_amount.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600">No recent orders</p>
          )}
        </div>
      </div>
    </div>
  );
}

