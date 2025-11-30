"use client";

import { useState } from "react";
import { ProductGrid } from "./product-grid";
import { Button } from "@/components/livekit/button";

interface ECommerceViewProps {
  onBackToVoice: () => void;
}

export function ECommerceView({ onBackToVoice }: ECommerceViewProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">E-commerce Store</h1>
            <p className="text-gray-600">Browse products and shop with voice or clicks</p>
          </div>
          <Button 
            onClick={onBackToVoice}
            variant="outline"
            className="flex items-center gap-2"
          >
            🎤 Back to Voice Chat
          </Button>
        </div>
      </div>
      
      <ProductGrid />
    </div>
  );
}