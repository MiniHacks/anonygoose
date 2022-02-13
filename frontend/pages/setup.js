import {Box, chakra, Flex, Heading, HStack, Text, useToast} from '@chakra-ui/react';
import {signOut, useSession} from 'next-auth/react';
import {PageLayout} from "../components/PageLayout";
import Layout from "../components/Layout";
import MyButton from "../components/MyButton";
import {useRouter} from "next/router";
import {useCallback, useEffect, useState} from "react";

export default function Home() {
    const {data: session, status} = useSession()
    const router = useRouter();
    const [rtmp, setRtmp] = useState("");
    const toast = useToast()

    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/");
        } else if (status === "authenticated") {
            fetch("/api/livestream/start").then(r => r.json()).then(r => {
                setRtmp(r.rtmp)
            })
        }
    }, [status])

    const otherPlatform = useCallback(() => {
        const platform = prompt("Please enter the RTMP uri for the other platform:");
        if (!platform) return;
        const q = new URLSearchParams({platform})
        fetch("/api/livestream/start?" + q.toString()).then(r => r.json()).then(() => {
            router.push('/stream');
        });
    }, [session])


    const HELLLLLL = useCallback(() => {
        if (!session) return;
        fetch("/api/livestream/start").then(r => r.json()).then(r => {
            const access_token = r.account.access_token;
            console.log("ACCESS TOKEN", access_token);
            gapi.load("client:auth2", function () {
                gapi.client.setToken(access_token)
                console.log("starting client:auth2");

                const client_id = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
                gapi.auth2.init({client_id});
                console.log("Initialized with client_id", client_id);

                const api_key = process.env.NEXT_PUBLIC_GOOGLE_API_KEY;
                gapi.client.setApiKey(api_key);
                console.log("Initialized with api_key", api_key);
                setTimeout(() => {
                    console.log("waited for 1 sec");
                    gapi.client.load("https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest")
                        .then(function () {
                                console.log("GAPI client loaded for API");
                                gapi.client.youtube.liveBroadcasts.insert({
                                    part: ['id,snippet,contentDetails,status'],
                                    resource: {
                                        snippet: {
                                            title: 'New Video:',
                                            scheduledStartTime: '2022-02-14T04:13:16+0000',
                                            description:
                                                'A description of your video stream. This field is optional.',
                                        },
                                        status: {
                                            privacyStatus: 'public',
                                            selfDeclaredMadeForKids: false,
                                        },
                                    },
                                })
                                    .then(function (response) {
                                            // Handle the results here (response.result has the parsed body).
                                            console.log("Response", response);
                                        },
                                        function (err) {
                                            console.error("Execute error", err);
                                        });

                            },
                            function (err) {
                                console.error("Error loading GAPI client for API", err);
                            });

                }, 1000)
            });

        })

    }, [session])


    return (<PageLayout wave={'40vh'}>
        <Layout pt={'13vh'}>
            <Flex justifyContent={"space-between"} alignItems={'center'} flexWrap={"wrap"}>
                <Box>
                    <Heading size={"2xl"} color={"#0A2540"} lineHeight={1.3}>
                        Your Input Stream
                    </Heading>
                    <Text color={'gray.600'}>
                        This is a secret link that you should enter into your streaming software.
                    </Text>
                    <HStack spacing={4} mt={4}>
                        {session && <>
                            <Text color={'gray.600'} fontFamily={"monospace"}>
                                {rtmp}
                            </Text>
                            <MyButton onClick={() => {
                                navigator.clipboard.writeText(rtmp)
                                toast({
                                    title: 'Copied RTMP URI!',
                                    variant: "subtle",
                                    position: "top",
                                    status: 'success',
                                    duration: 1000,
                                    isClosable: true,
                                })

                            }}>
                                Copy
                            </MyButton>
                        </>}
                    </HStack>
                </Box>
                <chakra.img src="https://placekitten.com/600/400" alt=""/>
            </Flex>
            <Flex justifyContent={"space-between"} alignItems={'center'} flexWrap={"wrap"} mt={40}>
                <Box>
                    <Heading size={"2xl"} color={"#0A2540"} lineHeight={1.3}>
                        Your Output Stream
                    </Heading>

                    <HStack spacing={4} mt={4}>
                        {session && <>
                            <MyButton onClick={HELLLLLL}>
                                Start Youtube Stream
                            </MyButton>
                            <Text color={'gray.600'} onClick={() => signOut()}>
                                as {session.user.name}
                            </Text>
                        </>}
                    </HStack>
                    <Text textDecorationStyle={"dotted!important"} textDecoration={"underline"} color={'gray.600'}
                          pt={4} onClick={() => otherPlatform()}>
                        Stream to another platform
                    </Text>
                </Box>
                <chakra.img src="https://placekitten.com/600/400" alt=""/>
            </Flex>
        </Layout>
    </PageLayout>);
}
