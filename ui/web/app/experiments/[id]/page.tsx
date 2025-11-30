import { Topbar } from "@/components/layout/topbar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { EquityCurve } from "@/components/charts/equity-curve"
import { DrawdownCurve } from "@/components/charts/drawdown-curve"
import { DistributionChart } from "@/components/charts/distribution-chart"
import { fetchExperiment } from "@/lib/api"
import { notFound } from "next/navigation"
import { format } from "date-fns"

interface ExperimentDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function ExperimentDetailPage({
  params,
}: ExperimentDetailPageProps) {
  const { id } = await params

  let experiment
  try {
    experiment = await fetchExperiment(id)
  } catch (error) {
    notFound()
  }

  const equityCurve = experiment.equity_curve || []
  const drawdownCurve = experiment.drawdown_curve || []
  const returnDistribution = experiment.return_distribution || []

  return (
    <div className="flex flex-col h-full">
      <Topbar title={`Experiment: ${experiment.id}`} />
      <div className="flex-1 p-6 space-y-6">
        {/* Summary Card */}
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Strategy</p>
                <p className="text-sm font-semibold">
                  {experiment.strategy_name}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Market</p>
                <p className="text-sm font-semibold">{experiment.market}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Period</p>
                <p className="text-sm font-semibold">
                  {format(new Date(experiment.start_date), "MMM dd, yyyy")} -{" "}
                  {format(new Date(experiment.end_date), "MMM dd, yyyy")}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Status</p>
                <Badge
                  variant={
                    experiment.status === "completed"
                      ? "default"
                      : experiment.status === "running"
                        ? "secondary"
                        : "destructive"
                  }
                >
                  {experiment.status}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Metrics Card */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Sharpe Ratio</p>
                <p className="text-2xl font-bold">
                  {experiment.metrics.sharpe.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Sortino Ratio</p>
                <p className="text-2xl font-bold">
                  {experiment.metrics.sortino.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Max Drawdown</p>
                <p className="text-2xl font-bold text-red-500">
                  {(experiment.metrics.max_drawdown * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">CAGR</p>
                <p className="text-2xl font-bold">
                  {(experiment.metrics.cagr * 100).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Hit Rate</p>
                <p className="text-2xl font-bold">
                  {(experiment.metrics.hit_rate * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Win Rate</p>
                <p className="text-2xl font-bold">
                  {(experiment.metrics.win_rate * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Parameters Card */}
        {Object.keys(experiment.parameters).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Parameters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {Object.entries(experiment.parameters).map(([key, value]) => (
                  <Badge key={key} variant="outline">
                    {key}: {String(value)}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Charts */}
        <div className="grid gap-4 md:grid-cols-2">
          {equityCurve.length > 0 && <EquityCurve data={equityCurve} />}
          {drawdownCurve.length > 0 && (
            <DrawdownCurve data={drawdownCurve} />
          )}
        </div>

        {returnDistribution.length > 0 && (
          <DistributionChart data={returnDistribution} />
        )}
      </div>
    </div>
  )
}


