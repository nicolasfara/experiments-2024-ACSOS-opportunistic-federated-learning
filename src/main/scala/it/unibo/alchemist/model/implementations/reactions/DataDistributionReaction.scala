package it.unibo.alchemist.model.implementations.reactions

import it.unibo.alchemist.model._
import it.unibo.alchemist.model.molecules.SimpleMolecule
import it.unibo.scafi.interop.PythonModules
import it.unibo.Utils._
import it.unibo.scafi.Sensors

class DataDistributionReaction[T, P <: Position[P]](
    environment: Environment[T, P],
    distribution: TimeDistribution[T],
    seed: Int,
    areas: Int,
    dataShuffle: Boolean,
    dataFraction: Double
) extends AbstractGlobalReaction(environment, distribution) {

  override protected def executeBeforeUpdateDistribution(): Unit = {
    val nodesCount = environment.getNodes.size()
    val dataDistribution = PythonModules.utils
      .dataset_to_nodes_partitioning(nodesCount, areas, seed, dataShuffle, dataFraction)
      .as[Map[Int, (List[Int], Set[Int])]]

    // I'm a dog, however I can't find a better solution to trigger the reconfiguration of the linking rule
    environment.getNodes.forEach(n => environment.moveNodeToPosition(n, environment.getPosition(n)))

    dataDistribution.foreach { case (id, (data, labels)) =>
      val node = environment.getNodeByID(id).manager
      node.put(Sensors.data, data.asInstanceOf[T])
      node.put(Sensors.labels, labels.asInstanceOf[T])
    }
  }

  override def initializationComplete(
      time: Time,
      environment: Environment[T, _]
  ): Unit = getTimeDistribution.update(Time.INFINITY, true, 0.0, environment)
}
