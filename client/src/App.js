import React, { useRef, useState, useEffect } from 'react'

import { Form, Button, Card, Alert, Navbar, Container, ListGroup, ListGroupItem } from 'react-bootstrap'
import SelectSearch, { fuzzySearch } from 'react-select-search'
import axios from 'axios'

function formatArray(array) {
      for(var i = 0; i < array.length; i++) {
          array[i] = {'name': array[i], 'value': array[i]}
      }

      return array
}

function App() {
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState([])
    const [fighterA, setFighterA] = useState('')
    const [fighterB, setFighterB] = useState('')    
    const [fighters, setFighters] = useState('')

    useEffect(() => {
        console.log(fighters)
        axios.get('https://sports-betting-odds-generator.herokuapp.com/get_fighters').then(response => {
            setFighters(response['data']['result'])
        }).catch(error => {
            setFighters('')
    })  
        console.log(fighters)
      }, []);

    async function handleSubmit(e) {
        e.preventDefault()

        setError('')
        setLoading(true)
        
        if (fighterA == '' || fighterB == '') {
            setError('Please select both fighters.')
        }
        else {
            await axios.get('https://sports-betting-odds-generator.herokuapp.com/generate_odds', {
                params: {
                    fighter_a: fighterA,
                    fighter_b: fighterB
                }
            }).then(response => {
                if (response['data']['status'] == 'success') {
                    setData(response['data']['result'])
                } else {
                    setError(response['data']['result'])
                }
            }).catch(error => {
                setError('Unknown error encountered.')
        })
        }

        setLoading(false)
    }

    return (
        <div>
            <Navbar bg='light' expand='lg'>
                <Container>
                    <Navbar.Brand >UFC Odds Generator</Navbar.Brand>
                    <Navbar.Toggle aria-controls='basic-navbar-nav' />
                </Container>
            </Navbar>
            <div className='d-flex align-items-center justify-content-center'
            style={{minHeight: '130vh'}}
            >
                <div className='w-100 d-flex align-items-center justify-content-center'>        
                    <div style={{minWidth: '600px'}}>
                        <Card>
                            <Card.Body>
                                <h2 className='text-center mb-4'>Fighter Input</h2>
                                {error && <Alert variant='danger'>{error}</Alert>}
                                <Form onSubmit={handleSubmit}>
                                    <Form.Group id='fighter-a'>
                                        <Form.Label>Fighter A</Form.Label>
                                        <SelectSearch 
                                            options={formatArray(fighters.split('---'))} 
                                            value={fighterA} 
                                            search 
                                            filterOptions={fuzzySearch}
                                            onChange={setFighterA} 
                                            placeholder='Select' 
                                            />                                        
                                    </Form.Group>

                                    <Form.Group id='fighter-b'>
                                        <Form.Label>Fighter B</Form.Label>
                                        <SelectSearch 
                                            options={formatArray(fighters.split('---'))} 
                                            value={fighterB} 
                                            search 
                                            filterOptions={fuzzySearch}
                                            onChange={setFighterB} 
                                            placeholder='Select' 
                                            />                                           
                                    </Form.Group>

                                    <Button disabled={loading} className='w-100 mt-4' type='submit'>
                                        Generate Odds
                                    </Button>                                           
                                </Form>
                            </Card.Body>
                        </Card>

                        <Card>
                            <Card.Body>
                                <h2 className='text-center mb-4'>Odds</h2>
                                <div className='w-100 d-flex align-items-center justify-content-center'>
                                    <Card style={{ width: '18rem' }}>
                                        <Card.Img variant='top' src={data.length > 0 ? data[4] : 'https://i.ibb.co/vYB53Kw/Untitled-1.png'} />
                                        <Card.Body>
                                            <Card.Title>{data.length > 0 ? fighterA : 'Fighter A'}</Card.Title>
                                            <Card.Text>{data.length > 0 ? (data[0] >= data[2] ? 'Favourite' : 'Underdog') : ''}</Card.Text>                                            
                                        </Card.Body>
                                        <ListGroup className='list-group-flush'>
                                            <ListGroupItem>Win Probability: {data.length > 0 ? data[0] : 50}%</ListGroupItem>
                                            <ListGroupItem>Moneyline Odds: {data.length > 0 ? data[1] : '+100'}</ListGroupItem>
                                        </ListGroup>
                                    </Card>

                                    <Card style={{ width: '18rem' }}>
                                        <Card.Img variant='top' src={data.length > 0 ? data[5] : 'https://i.ibb.co/vYB53Kw/Untitled-1.png'} />
                                        <Card.Body>
                                            <Card.Title>{data.length > 0 ? fighterB : 'Fighter B'}</Card.Title>
                                            <Card.Text>{data.length > 0 ? (data[0] >= data[2] ? 'Underdog' : 'Favourite') : ''}</Card.Text>
                                        </Card.Body>
                                        <ListGroup className='list-group-flush'>
                                            <ListGroupItem>Win Probability: {data.length > 0 ? data[2] : 50}%</ListGroupItem>
                                            <ListGroupItem>Moneyline Odds: {data.length > 0 ? data[3] : '+100'}</ListGroupItem>
                                        </ListGroup>
                                    </Card> 
                                </div>                               
                            </Card.Body>
                        </Card>                
                    </div>
                </div>
            </div>   
        </div>
    );
}

export default App;
