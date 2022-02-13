import {Box, chakra, Flex, Heading, HStack, Text, useToast} from '@chakra-ui/react';
import {signOut, useSession} from 'next-auth/react';
import {PageLayout} from "../components/PageLayout";
import Layout from "../components/Layout";
import MyButton from "../components/MyButton";
import dynamic from "next/dynamic";
import {useRouter} from "next/router";
import {useCallback, useEffect, useState} from "react";

const FileUpload = dynamic(() => import("../components/FileUpload"), {ssr: false})

export default function Home() {
    const [youtubeIngestionUrl, setYoutubeIngestionUrl] = useState('')
    const [youtubeStreamName, setYoutubeStreamName] = useState('')
    const [showDropZone, setShowDropZone] = useState(false);
    const [streamId, setStreamId] = useState('')
    const [broadcastId, setBroadcastId] = useState('')
    const {data: session, status} = useSession()
    const router = useRouter();
    const [rtmp, setRtmp] = useState("");
    const [images, setImages] = useState([])
    const toast = useToast()


    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/");
        } else if (status === "authenticated") {
            fetch("/api/livestream/start").then(r => r.json()).then(r => {
                setRtmp(r.rtmp)
            })
            fetch("/api/images").then(r => r.json()).then(r => {
                setImages(r.map(i => i.path))
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


    const HELLLLLL = useCallback(async () => {
        console.log("fuck")
        if (!session) return;
        console.log("me")
        const response = await fetch("/api/livestream/start")
        const data = await response.json()
        const access_token = data.account.access_token;
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
                    .then(() => {
                            console.log("GAPI client loaded for API");
                            gapi.client.youtube.liveBroadcasts.insert({
                                part: ['id,snippet,contentDetails,status'],
                                resource: {
                                    snippet: {
                                        title: 'New Video:',
                                        scheduledStartTime: `${new Date().toISOString()}`,
                                        description:
                                            'A description of your video stream. This field is optional.',
                                    },
                                    status: {
                                        privacyStatus: 'public',
                                        selfDeclaredMadeForKids: false,
                                    },
                                },
                            })
                                .then(async (response) => {
                                        // Handle the results here (response.result has the parsed body).
                                        const id = response.result.id;
                                        createStream()
                                        bindBroadcastToStream(id)
                                        /*
                                        setTimeout(() => {
                                            transitionToLive(id)
                                        }, 5000)
                                        */
                                        const r = await listLivestreams()
                                        console.log(r.result)
                                    },
                                    (err) => {
                                        console.error("Execute error", err);
                                    });

                        },
                        (err) => {
                            console.error("Error loading GAPI client for API", err);
                        });

            }, 1000)
        })

    }, [session])

    const bindBroadcastToStream = (id) => {
        return gapi.client.youtube.liveBroadcasts
            .bind({
                part: ['id,snippet,contentDetails,status'],
                id: id,
                streamId: streamId,
            })
            .then((res) => {
                //console.log('Response', res)
                console.log(res.result.id)
            })
            .catch((err) => {
                console.error('Execute error', err)
            })
    }

    const createStream = () => {
        return gapi.client.youtube.liveStreams
            .insert({
                part: ['snippet,cdn,contentDetails,status'],
                resource: {
                    snippet: {
                        title: "Your new video stream's name",
                        description:
                            'A description of your video stream. This field is optional.',
                    },
                    cdn: {
                        frameRate: 'variable',
                        ingestionType: 'rtmp',
                        resolution: 'variable',
                        format: '',
                    },
                    contentDetails: {
                        isReusable: true,
                        enableAutoStart: true,
                        broadcastType: "persistent"
                    },
                },
            })
            .then((res) => {
                //console.log('Response', res)

                setStreamId(res.result.id)
                console.log('streamID' + res.result.id)

                setYoutubeIngestionUrl(res.result.cdn.ingestionInfo.ingestionAddress)
                console.log(res.result.cdn.ingestionInfo.ingestionAddress)

                setYoutubeStreamName(res.result.cdn.ingestionInfo.streamName)
                console.log(res.result.cdn.ingestionInfo.streamName)
            })
            .catch((err) => {
                console.log('Execute error', err)
            })
    }

    const listLivestreams = async () => {
        return gapi.client.youtube.liveStreams.list({
            part: ['snippet,id,cdn,status'],
            mine: true
        })
    }

    const transitionToLive = (id) => {
        return gapi.client.youtube.liveBroadcasts
            .transition({
                part: ['id,snippet,contentDetails,status'],
                broadcastStatus: 'live',
                id: id,
            })
            .then((res) => {
                // Handle the results here (response.result has the parsed body).
                console.log('Response', res)
            })
            .catch((err) => {
                console.log('Execute error', err)
            })
    }

    return (<PageLayout wave={'50vh'}>
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
                <chakra.img src="/chonk_stack.png" maxW={"40vw"} mr={'-100px'} alt=""/>
            </Flex>
            <Flex justifyContent={"space-between"} alignItems={'center'} flexWrap={"wrap"}>
                <Box>
                    <Heading size={"2xl"} color={"#0A2540"} lineHeight={1.3}>
                        Your Team <MyButton onClick={() => setShowDropZone(pv => !pv)}>+</MyButton>
                    </Heading>
                    <Text color={'gray.600'} mb={3}>
                        Submit pictures of people to whitelist.
                    </Text>
                    {showDropZone && <FileUpload onFileAccepted={data => {
                        const uploadPictureHandler = async (file) => {
                            const pictureData = new FormData();
                            pictureData.append('image', file);
                            try {
                                const response = await fetch('/api/upload', {
                                    method: 'POST',
                                    body: pictureData,
                                });
                                const data = await response.json();
                                if (!response.ok) {
                                    throw data;
                                }
                                console.log(data);
                                router.reload();
                            } catch (error) {
                                console.log(error.message);
                            }
                        };
                        uploadPictureHandler(data[0])
                    }}/>}
                    <HStack spacing={4} mt={4}>
                        {images.map(i => <chakra.img borderRadius={"sm"} width={250} src={process.env.NEXT_PUBLIC_IMG_URL+i} key={i}/>)}
                    </HStack>
                </Box>
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
            </Flex>
        </Layout>
    </PageLayout>);
}
