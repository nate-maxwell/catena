from catena import api

import stats_pane


def install_statistics_pane() -> None:
    pane = stats_pane.GraphStatsPane(api.get_reference_to_base_client())
    pane.hide()
    menu = api.add_menu("View")
    api.add_toolbar_menu_item(menu, "Statistics Pane", pane.toggle_visibility)


install_statistics_pane()
