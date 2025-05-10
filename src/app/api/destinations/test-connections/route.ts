import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const data = await request.json()
  
  try {
    const response = await fetch('http://localhost:8000/destinations/test-connection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    const result = await response.json()
    
    return NextResponse.json(result, {
      status: response.status,
    })
  } catch (error) {
    console.error('Error forwarding request to API:', error)
    return NextResponse.json(
      { detail: 'Failed to connect to backend service' },
      { status: 500 }
    )
  }
}