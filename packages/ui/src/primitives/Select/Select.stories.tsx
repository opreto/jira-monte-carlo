import type { Meta, StoryObj } from '@storybook/react'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from './Select'

const meta = {
  title: 'Primitives/Select',
  component: Select,
  tags: ['autodocs'],
} satisfies Meta<typeof Select>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => (
    <Select>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Select a fruit" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="apple">Apple</SelectItem>
        <SelectItem value="banana">Banana</SelectItem>
        <SelectItem value="orange">Orange</SelectItem>
        <SelectItem value="mango">Mango</SelectItem>
        <SelectItem value="grape">Grape</SelectItem>
      </SelectContent>
    </Select>
  ),
}

export const WithGroups: Story = {
  render: () => (
    <Select defaultValue="apple">
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Select an item" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Fruits</SelectLabel>
          <SelectItem value="apple">Apple</SelectItem>
          <SelectItem value="banana">Banana</SelectItem>
          <SelectItem value="orange">Orange</SelectItem>
        </SelectGroup>
        <SelectSeparator />
        <SelectGroup>
          <SelectLabel>Vegetables</SelectLabel>
          <SelectItem value="carrot">Carrot</SelectItem>
          <SelectItem value="potato">Potato</SelectItem>
          <SelectItem value="tomato">Tomato</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  ),
}

export const SprintSelection: Story = {
  render: () => (
    <div className="space-y-2">
      <label className="text-sm font-medium">Select Sprint</label>
      <Select defaultValue="sprint-42">
        <SelectTrigger className="w-[250px]">
          <SelectValue placeholder="Choose a sprint" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Current Sprint</SelectLabel>
            <SelectItem value="sprint-42">Sprint 42 (Current)</SelectItem>
          </SelectGroup>
          <SelectSeparator />
          <SelectGroup>
            <SelectLabel>Previous Sprints</SelectLabel>
            <SelectItem value="sprint-41">Sprint 41</SelectItem>
            <SelectItem value="sprint-40">Sprint 40</SelectItem>
            <SelectItem value="sprint-39">Sprint 39</SelectItem>
            <SelectItem value="sprint-38">Sprint 38</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  ),
}

export const TeamSelection: Story = {
  render: () => (
    <Select>
      <SelectTrigger className="w-[300px]">
        <SelectValue placeholder="Select a team" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="engineering">Engineering</SelectItem>
        <SelectItem value="product">Product</SelectItem>
        <SelectItem value="design">Design</SelectItem>
        <SelectItem value="qa">Quality Assurance</SelectItem>
        <SelectItem value="devops">DevOps</SelectItem>
      </SelectContent>
    </Select>
  ),
}

export const DateRangePresets: Story = {
  render: () => (
    <Select defaultValue="last-30">
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Select date range" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="today">Today</SelectItem>
        <SelectItem value="yesterday">Yesterday</SelectItem>
        <SelectItem value="last-7">Last 7 days</SelectItem>
        <SelectItem value="last-30">Last 30 days</SelectItem>
        <SelectItem value="last-90">Last 90 days</SelectItem>
        <SelectItem value="this-quarter">This quarter</SelectItem>
        <SelectItem value="last-quarter">Last quarter</SelectItem>
        <SelectItem value="custom">Custom range...</SelectItem>
      </SelectContent>
    </Select>
  ),
}

export const Disabled: Story = {
  render: () => (
    <Select disabled>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Disabled select" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="option1">Option 1</SelectItem>
        <SelectItem value="option2">Option 2</SelectItem>
      </SelectContent>
    </Select>
  ),
}

export const WithDisabledItems: Story = {
  render: () => (
    <Select>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Select status" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="active">Active</SelectItem>
        <SelectItem value="pending">Pending</SelectItem>
        <SelectItem value="archived" disabled>
          Archived (Unavailable)
        </SelectItem>
        <SelectItem value="deleted" disabled>
          Deleted (Unavailable)
        </SelectItem>
      </SelectContent>
    </Select>
  ),
}