import { Box } from '@chakra-ui/react'

export default function CustomCard({title, description}) {
  return (
    <Box maxW='sm' borderWidth='1px' overflow='auto'>
      This is the title: {title}
      I put text here!
      This is the description: {description}

    </Box>
  )
}