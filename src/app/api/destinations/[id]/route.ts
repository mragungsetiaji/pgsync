import { NextResponse } from 'next/server'

export async function PUT(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id
  const data = await request.json()
  
  try {
    const response = await fetch(`http://localhost:8000/destinations/${id}`, {
      method: 'PUT',
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

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id
  
  try {
    const response = await fetch(`http://localhost:8000/destinations/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (response.status === 204) {
      return new NextResponse(null, { status: 204 })
    }
    
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

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id
  
  try {
    const response = await fetch(`http://localhost:8000/destinations/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
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