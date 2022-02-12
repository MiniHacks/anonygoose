import { SimpleGrid, GridItem } from '@chakra-ui/react'
import Card from "./Card.js";

export default function FeatureGrid() {
  return (
    <SimpleGrid columns={2} spacing={4}>
      <Card title="Privacy" description="ML blurs faces which makes everything private. Wow."/>
      <Card title="No faces" description="Don't have to see people. Wow this is good text.?"/>
      <Card title="Good" description="Good? Good. Good! Probably."/> 
      <Card title="Socially ethical" description="I hope the judges are compelled by how ethical this is."/>
    </SimpleGrid>
  )
}