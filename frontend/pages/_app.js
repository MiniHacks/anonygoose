import {ChakraProvider} from "@chakra-ui/react"
import {SessionProvider} from "next-auth/react"


function MyApp({Component, pageProps: {session, ...pageProps}}) {
    return (
        <SessionProvider session={session}>
            <script src="https://apis.google.com/js/api.js"/>
            <script src="https://embed.twitch.tv/embed/v1.js"></script>
            <ChakraProvider>
                <Component {...pageProps} />
            </ChakraProvider>
        </SessionProvider>

    )
}

export default MyApp
