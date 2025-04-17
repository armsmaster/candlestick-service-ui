import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from 'react-bootstrap';
import Stack from 'react-bootstrap/Stack';

function SignInWithGoogle({ url, csrf_token }) {

    return (
        <>
            <form action={url} method="GET">
                <input type="hidden" name="csrf_token" value={csrf_token} />
                <button class="gsi-material-button" type='submit'>
                    <div class="gsi-material-button-state"></div>
                    <div class="gsi-material-button-content-wrapper">
                        <div class="gsi-material-button-icon">
                            <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" xmlns:xlink="http://www.w3.org/1999/xlink" style={{ display: "block" }}>
                                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
                                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
                                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                                <path fill="none" d="M0 0h48v48H0z"></path>
                            </svg>
                        </div>
                        <span class="gsi-material-button-contents">Sign in with Google</span>
                        <span style={{ display: "none" }}>Sign in with Google</span>
                    </div>
                </button>
            </form>
        </>
    )
}

function SignInWithYandex({ url, csrf_token }) {

    return (
        <>
            <form action={url} method="GET">
                <input type="hidden" name="csrf_token" value={csrf_token} />
                <button class="gsi-material-button" type='submit'>
                    <div class="gsi-material-button-state"></div>
                    <div class="gsi-material-button-content-wrapper">
                        <div class="gsi-material-button-icon">
                            <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" xmlns:xlink="http://www.w3.org/1999/xlink" style={{ display: "block" }}>

                                <rect width="44" height="44" rx="22" fill="#FC3F1D"></rect>
                                <path d="M25.2438 12.3208H23.0173C19.2005 12.3208 17.292 14.2292 17.292 17.0919C17.292 20.2726 18.5643 21.863 21.427 23.7714L23.6535 25.3618L17.292 35.222H12.2029L18.2463 26.316C14.7475 23.7714 12.839 21.5449 12.839 17.41C12.839 12.3208 16.3378 8.82202 23.0173 8.82202H29.6969V35.222H25.2438V12.3208Z" fill="white"></path>
                            </svg>
                        </div>
                        <span class="gsi-material-button-contents">Sign in with Yandex</span>
                        <span style={{ display: "none" }}>Sign in with Yandex</span>
                    </div>
                </button>
            </form>
        </>
    )
}

function SignOutComponent({ sessionData, setSessionData }) {
    return (
        <>
            <Navbar.Text>
                <Stack direction='horizontal' gap={1}>
                    <Button variant='outline-dark' disabled >
                        {sessionData.user_email}
                    </Button>
                    <Button variant='outline-dark' onClick={() => {
                        axios.delete('/ui-backend/session/')
                            .then(response => {
                                setSessionData(response.data);
                            })
                            .catch(error => {
                                console.error(error);
                            });
                    }}>Sign Out</Button>
                </Stack>
            </Navbar.Text>
        </>
    )
}

function SignInComponent({ csrf_token }) {
    return (
        <>
            <Navbar.Text>
                <Stack direction='horizontal' gap={1}>
                    <SignInWithGoogle url={"/ui-backend/oauth2/google/auth/?csrf_token="} csrf_token={csrf_token} />
                    <SignInWithYandex url={"/ui-backend/oauth2/yandex/auth/?csrf_token="} csrf_token={csrf_token} />
                </Stack>
                {/* <a href={"/ui-backend/oauth2/yandex/auth/?csrf_token=" + csrf_token}>Yandex</a> */}
                {/* <a href={"/ui-backend/oauth2/yandex/auth/?csrf_token=" + csrf_token}>Yandex</a> */}
            </Navbar.Text>
        </>
    )
}


function NavbarComponent() {

    const [sessionData, setSessionData] = useState({});

    useEffect(() => {
        axios.get('/ui-backend/session/')
            .then(response => {
                setSessionData(response.data);
            })
            .catch(error => {
                console.error(error);
            });
    }, []);

    return (
        <Navbar className="bg-body-tertiary">
            <Container>
                <Navbar.Brand>Candlestick Service UI</Navbar.Brand>
                <Navbar.Toggle />
                <Navbar.Collapse className="justify-content-end">
                    {sessionData.is_authenticated ?
                        <SignOutComponent sessionData={sessionData} setSessionData={setSessionData} /> :
                        <SignInComponent csrf_token={sessionData.csrf_token} />
                    }
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
}

export default NavbarComponent;