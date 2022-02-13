import {Box} from "@chakra-ui/react";

const Layout = ({children, ...props}) => <Box mx={'max(2px, 10%)'} {...props}>
    {children}
</Box>
export default Layout;
