import {Box} from "@chakra-ui/react";
import Footer from "./Footer";
import Head from "next/head";
import Wave from "./Wave";

export const PageLayout = ({children, wave}) => (<Box>
    <Head>
        <title>Reveal the story, mot those around you | Anonynews</title>
        <meta
            name='description'
            content="Created for Hack For Humanity 2022"
        />
        <link rel='icon' href='/favicon.ico'/>
    </Head>

    <Box position={"absolute"} zIndex={-1} top={wave}>
        <Wave/>
    </Box>

    <Box zIndex={2} minH={"calc(100vh - 100px)"}>
        {children}
    </Box>
    <Footer/>
    <style>{`body{background-color: #FFF2FE}`}</style>
</Box>)
