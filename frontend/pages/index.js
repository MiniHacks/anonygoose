import {chakra, Box, Flex, Heading, HStack, Text, VStack} from '@chakra-ui/react';
import {signIn, signOut} from 'next-auth/react';
import FeatureGrid from '../components/FeatureGrid';
import {PageLayout} from "../components/PageLayout";
import Layout from "../components/Layout";
import MyButton from "../components/MyButton";
import { useSession } from "next-auth/react"
import {useRouter} from "next/router";
import {useEffect} from "react";

export default function Home() {
    const { data: session, status } = useSession();

    const router = useRouter();

    useEffect(() => {
        if(status==="authenticated") {
            router.push("/setup");
        }
    }, [status])
    return (<PageLayout wave={'40vh'}>
        <Layout pt={'13vh'}>
            <Flex justifyContent={"space-between"} alignItems={'center'} flexWrap={"wrap"}>
                <Box>
                    <Heading size={"2xl"} color={"#0A2540"} lineHeight={1.3}>
                        Reveal the story,<br/>Not those around you
                    </Heading>
                    <Text color={"#425466"} fontSize={"20px"} mt={3}>
                        <strong>Anonynews</strong> uses machine learning to protect<br/>the privacy of everyone on the scene
                    </Text>
                    <HStack spacing={4} mt={4}>
                        {!session && <MyButton onClick={() => signIn('google')}>
                            Sign in with YouTube
                        </MyButton>}
                        {session && <>
                            <MyButton onClick={() => router.push("/setup")}>
                                Start Stream
                            </MyButton>
                            <Text color={'gray.600'} onClick={() => signOut()}>
                                as {session.user.name}
                            </Text>
                        </>}
                    </HStack>
                </Box>
                <chakra.img src="/chonk_stack.png" maxW={"40vw"} mr={'-100px'} alt=""/>
            </Flex>
            <Heading mt={40} textAlign={"center"} size={"2xl"} mb={16}>Features</Heading>
            <FeatureGrid/>
            <Heading mt={20} textAlign={"center"} size={"2xl"} mb={16}>See it in action!</Heading>
            <Box mt={20}>
                <iframe
                    src="https://player.twitch.tv/?channel=montressorempire74&parent=anony.news"
                    height="800px"
                    width="100%"
                    allowFullScreen="true">
                </iframe>
            </Box>
        </Layout>
    </PageLayout>);
}
