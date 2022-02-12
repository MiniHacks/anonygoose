import Head from 'next/head'
import io from 'socket.io-client';
import {Box, Heading, VStack} from "@chakra-ui/react";
import {useEffect, useState} from "react";
import {signIn} from "next-auth/react";

export default function Home() {
    const backendURL = process.env.NEXT_PUBLIC_BACKEND;
    const [socket, setSocket] = useState(null);
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const newSocket = io(backendURL);
        setSocket(newSocket);

        newSocket.on("message", msg => setMessages(pv => [...pv, msg]))

        return () => newSocket.close();
    }, [])

    return (
        <Box>
            <Head>
                <title>Create Next App</title>
                <meta name="description" content="Generated by create next app"/>
                <link rel="icon" href="/favicon.ico"/>
            </Head>

            <VStack justifyContent={'center'} alignItems={'center'} minH={'100vh'} bg={'green.300'}>
                <button onClick={() => signIn("google")}>hi</button>
                <Heading>Messages:</Heading>
                {!messages.length && <pre>Connecting to socket...</pre>}
                <pre>{JSON.stringify(messages, null, 4)}</pre>
            </VStack>
        </Box>
    )
}
