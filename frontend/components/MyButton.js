import {Button} from "@chakra-ui/react";

const MyButton = ({children, ...props}) => (<Button height='48px'
                                                    borderRadius='6px'
                                                    boxShadow={'rgba(45, 35, 66, .4) 0 2px 4px,rgba(45, 35, 66, .3) 0 7px 13px -3px,rgba(58, 65, 111, .5) 0 -3px 0 inset'}
                                                    transition={'box-shadow .15s,transform .15s'}
                                                    bgGradient='linear(to-bl, pink.50, #FFD8FB)'
                                                    _hover={{
                                                        boxShadow: 'rgba(45, 35, 66, .4) 0 2px 6px,rgba(45, 35, 66, .3) 0 7px 23px -3px,rgba(58, 65, 111, .5) 0 -2px 0 inset'
                                                    }}
                                                    _active={{
                                                        background: "transparent"
                                                    }} {...props}>
    {children}
</Button>)
export default MyButton
