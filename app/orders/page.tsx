'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface OrderItem {
  order_item_id: number;
  item_id: number;
  description: string;
  price: number;
  quantity?: number;
  isbn?: string;
  item_type?: string;
}

interface Order {
  order_id: number;
  order_amount: number;
  item_count: number;
  order_date: string;
  customer_id: number;
  promotion_id: number | null;
  items: OrderItem[];
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await fetch('/api/py/orders');
      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
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
        <h1 className="text-3xl font-bold text-gray-900">Orders</h1>
      </div>
      
      <div className="space-y-4">
        {orders.map((order) => (
          <div key={order.order_id} className="border border-gray-300 rounded-lg p-6 shadow-md bg-white">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Order #{order.order_id}</h2>
                <p className="text-gray-600">Date: {new Date(order.order_date).toLocaleDateString()}</p>
                <p className="text-gray-600">Customer ID: {order.customer_id}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">${order.order_amount.toFixed(2)}</p>
                <p className="text-gray-600">{order.item_count} items</p>
              </div>
            </div>
            
            <div className="mt-4">
              <h3 className="font-semibold mb-2 text-gray-900">Items:</h3>
              <ul className="space-y-2">
                {order.items.map((item, index) => {
                  const quantity = item.quantity || 1;
                  const totalPrice = item.price * quantity;
                  return (
                    <li key={item.order_item_id || index} className="flex justify-between text-gray-700">
                      <span>
                        {item.description || `Item #${item.item_id}`}
                        {quantity > 1 && <span className="text-gray-500 ml-2">(x{quantity})</span>}
                      </span>
                      <span>${totalPrice.toFixed(2)}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

