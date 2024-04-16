package it.unibo.alchemist.model.implementations.reactions

import it.unibo.alchemist.model._
import it.unibo.alchemist.model.molecules.SimpleMolecule
import it.unibo.scafi.interop.PythonModules

class DataDistributionReaction[T, P <: Position[P]](
    environment: Environment[T, P],
    distribution: TimeDistribution[T],
    seed: Int,
    areas: Int,
    dataShuffle: Boolean
) extends AbstractGlobalReaction(environment, distribution) {

  override protected def executeBeforeUpdateDistribution(): Unit = {
    val nodesCount = environment.getNodes.size()
    val dataDistribution = PythonModules.utils
      .dataset_to_nodes_partitioning(nodesCount, areas, seed, dataShuffle)
      .as[Map[Int, List[Int]]]

    dataDistribution.foreach { case (id, data) =>
      val node = environment.getNodeByID(id)
      node.setConcentration(new SimpleMolecule("data"), data.asInstanceOf[T])
    }
  }

  override def initializationComplete(
      time: Time,
      environment: Environment[T, _]
  ): Unit = getTimeDistribution.update(Time.INFINITY, true, 0.0, environment)
}