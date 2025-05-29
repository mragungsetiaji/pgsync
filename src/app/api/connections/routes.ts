import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/connections/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    })
    
    console.log('API response status (GET connections):', response.status)
    
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
    console.error('Error in connections API route (GET):', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const data = await request.json()
    
    console.log('Creating connection:', JSON.stringify(data, null, 2))
    
    const response = await fetch('http://localhost:8000/connections/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    console.log('API response status (POST connection):', response.status)
    
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
    
    try {
      const responseText = await response.text()
      
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
    console.error('Error in connections API route (POST):', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}