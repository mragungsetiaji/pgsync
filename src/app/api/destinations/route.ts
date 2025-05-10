import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Create a request to fetch destinations from your API
    const response = await fetch('http://localhost:8000/destinations/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // Don't cache the response
    })
    
    console.log('API response status (GET):', response.status)
    
    // Handle non-JSON responses or empty responses
    if (!response.ok) {
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json()
        console.error('API error response:', errorData)
        return NextResponse.json(errorData, { status: response.status })
      } else {
        const errorText = await response.text()
        console.error('API error text:', errorText)
        return NextResponse.json(
          { detail: errorText || 'Error from API' },
          { status: response.status }
        )
      }
    }
    
    // Parse response with error handling
    try {
      const responseText = await response.text()
      
      if (!responseText) {
        return NextResponse.json([], { status: 200 })
      }
      
      const result = JSON.parse(responseText)
      return NextResponse.json(result, { status: response.status })
    } catch (parseError) {
      console.error('Error parsing API response:', parseError)
      return NextResponse.json(
        { detail: 'Failed to parse API response' },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('Error in destinations API route (GET):', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const data = await request.json()
    
    console.log('Received data:', JSON.stringify(data, null, 2))
    
    // Create a new request with the same body
    const response = await fetch('http://localhost:8000/destinations/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    console.log('API response status:', response.status)
    
    // Handle non-JSON responses or empty responses
    if (!response.ok) {
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json()
        console.error('API error response:', errorData)
        return NextResponse.json(errorData, { status: response.status })
      } else {
        const errorText = await response.text()
        console.error('API error text:', errorText)
        return NextResponse.json(
          { detail: errorText || 'Error from API' },
          { status: response.status }
        )
      }
    }
    
    // Parse response with error handling
    try {
      const responseText = await response.text()
      console.log('API response body:', responseText)
      
      if (!responseText) {
        return NextResponse.json({ detail: 'Empty response from API' }, { status: 204 })
      }
      
      const result = JSON.parse(responseText)
      return NextResponse.json(result, { status: response.status })
    } catch (parseError) {
      console.error('Error parsing API response:', parseError)
      return NextResponse.json(
        { detail: 'Failed to parse API response' },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('Error in destinations API route:', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}