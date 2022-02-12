import { Box, Heading, Text } from '@chakra-ui/react'
import { SettingsIcon } from '@chakra-ui/icons'

export default function CustomCard({title, description}) {
  return (
    <Box maxW='sm' borderWidth='1px' overflow='auto'>
      <SettingsIcon color='pink.500'/>
      <Heading as='h3' size='md'> 
        {title}
      </Heading>
      <Text>
        {description}
      </Text>

    </Box>
  )
}