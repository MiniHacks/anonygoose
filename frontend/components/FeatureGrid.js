import {Grid, GridItem } from '@chakra-ui/react'
import Card from "./Card.js";

export default function FeatureGrid() {
  return (
    <Grid templateColumns='repeat(2, 1fr)' gap={4}>
      <GridItem w='100%' h='10' bg='blue.500'>
        <Card title="Test" description="test?"/>
      </GridItem>
      <GridItem w='100%' h='10' bg='blue.500'/>
      <GridItem w='100%' h='10' bg='blue.500'/>
      <GridItem w='100%' bg='blue.500'/>
    </Grid>
  )
}