import { useState } from 'react'
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import NavbarComponent from './navbar';
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <NavbarComponent />

      {/* <Container fluid>
        <Row>
          <Col>
            <Button variant='primary' onClick={() => setCount((count) => count + 1)}>
              count: {count}
            </Button>
          </Col>
        </Row>
      </Container> */}
    </>
  )
}

export default App
