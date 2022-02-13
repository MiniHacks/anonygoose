import { Box, Heading, Text } from '@chakra-ui/react'
import { SettingsIcon } from '@chakra-ui/icons'

export default function CustomCard({title, description}) {
  return (
    <Box overflow='auto' bg={'rgba(255,255,255,0.7)'} p={5} borderRadius={"lg"}>
      <Heading as='h3' size='md'>
        <SettingsIcon mr='3' color='pink.500'/>
        {title}
      </Heading>
      <Text ml='8' mt='2'>
        {description}
      </Text>
    </Box>
  )
}
