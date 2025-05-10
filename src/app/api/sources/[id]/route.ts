import { NextResponse } from 'next/server'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id
    
    const response = await fetch(`http://localhost:8000/sources/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    })
    
    console.log(`API response status (GET source ${id}):`, response.status)
    
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
        return NextResponse.json({}, { status: 204 })
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
    console.error('Error in source API route (GET):', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id
    const data = await request.json()
    
    const response = await fetch(`http://localhost:8000/sources/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    console.log(`API response status (PUT source ${id}):`, response.status)
    
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
    console.error('Error in source API route (PUT):', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id
    
    const response = await fetch(`http://localhost:8000/sources/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    console.log(`API response status (DELETE source ${id}):`, response.status)
    
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
    
    if (response.status === 204) {
      return new NextResponse(null, { status: 204 })
    }
    
    try {
      const responseText = await response.text()
      
      if (!responseText) {
        return NextResponse.json({ success: true }, { status: 200 })
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
    console.error('Error in source API route (DELETE):', error)
    return NextResponse.json(
      { detail: 'Failed to process request' },
      { status: 500 }
    )
  }
}