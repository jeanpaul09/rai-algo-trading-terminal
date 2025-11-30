import { Topbar } from "@/components/layout/topbar"
import { ExperimentsTable } from "@/components/tables/experiments-table"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { fetchExperiments, fetchStrategies } from "@/lib/api"

export default async function ExperimentsPage() {
  const [experiments, strategies] = await Promise.all([
    fetchExperiments(),
    fetchStrategies(),
  ])

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Experiment Lab" />
      <div className="flex-1 p-6 space-y-6">
        {/* Filters */}
        <div className="flex gap-4 items-center">
          <Input
            placeholder="Search experiments..."
            className="max-w-sm"
          />
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by strategy" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Strategies</SelectItem>
              {strategies.map((strategy) => (
                <SelectItem key={strategy.name} value={strategy.name}>
                  {strategy.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="running">Running</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Experiments Table */}
        <ExperimentsTable experiments={experiments} />
      </div>
    </div>
  )
}


