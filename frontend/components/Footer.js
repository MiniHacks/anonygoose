import {chakra} from "@chakra-ui/react"
import Layout from "./Layout";

const Footer = () => (<Layout p={4}>
    Created by the <chakra.a textDecoration={"underline"} textDecorationStyle={"dotted"}
                             _hover={{textDecorationStyle: "solid"}}
                             href="https://github.com/minihacks">Minihacks</chakra.a> team for <chakra.a
    textDecoration={"underline"} textDecorationStyle={"dotted"}
    _hover={{textDecorationStyle: "solid"}}    href="https://hackforhumanity.io/">Hack for Humanity</chakra.a> 2022 &hearts;
</Layout>)
export default Footer;
