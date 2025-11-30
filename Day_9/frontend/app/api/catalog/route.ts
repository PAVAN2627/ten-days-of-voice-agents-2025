import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Read catalog from backend
    const catalogPath = path.join(process.cwd(), '..', 'backend', 'catalog.json');
    const catalogData = fs.readFileSync(catalogPath, 'utf8');
    const catalog = JSON.parse(catalogData);
    
    return NextResponse.json(catalog);
  } catch (error) {
    console.error('Failed to read catalog:', error);
    
    // Fallback catalog
    const fallbackCatalog = {
      products: [
        {
          id: "mug-001",
          name: "Stoneware Coffee Mug",
          price: 800,
          currency: "INR",
          category: "mug",
          color: "white",
          description: "Premium ceramic coffee mug with ergonomic handle"
        },
        {
          id: "mug-002",
          name: "Glass Coffee Mug",
          price: 600,
          currency: "INR",
          category: "mug",
          color: "clear",
          description: "Transparent borosilicate glass mug"
        },
        {
          id: "tshirt-001",
          name: "Cotton T-Shirt",
          price: 1200,
          currency: "INR",
          category: "clothing",
          color: "blue",
          size: "M",
          description: "100% cotton casual t-shirt"
        },
        {
          id: "hoodie-001",
          name: "Black Hoodie",
          price: 2500,
          currency: "INR",
          category: "clothing",
          color: "black",
          size: "M",
          description: "Comfortable cotton hoodie with front pocket"
        },
        {
          id: "book-001",
          name: "Python Programming Guide",
          price: 1500,
          currency: "INR",
          category: "books",
          description: "Complete guide to Python programming for beginners"
        }
      ]
    };
    
    return NextResponse.json(fallbackCatalog);
  }
}