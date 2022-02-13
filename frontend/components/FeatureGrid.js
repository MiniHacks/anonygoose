import { SimpleGrid, GridItem } from '@chakra-ui/react'
import Card from "./Card.js";

export default function FeatureGrid() {
  return (
    <SimpleGrid columns={2} spacing={12}>
      <Card title="Facial Detection" description="Machine learning automatically blurs the faces of those at risk."/>
      <Card title="Secure Whitelist" description="One example image and it's business as usual for reporters."/>
      <Card title="Seamless Workflow" description="Export your RTMP URI in as few as three clicks."/>
      <Card title="Cute Goose" description="Doesn't he look good in a suit?"/>
    </SimpleGrid>
  )
}
