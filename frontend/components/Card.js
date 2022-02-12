import { Box, Heading, Text } from '@chakra-ui/react'
import { SettingsIcon } from '@chakra-ui/icons'

export default function CustomCard({title, description}) {
  return (
    <Box maxW='sm' overflow='auto'>
      <Heading as='h3' size='md'> 
        <SettingsIcon color='pink.500'/>
        {title}
      </Heading>
      <Text>
        {description}
      </Text>

    </Box>
  )
}