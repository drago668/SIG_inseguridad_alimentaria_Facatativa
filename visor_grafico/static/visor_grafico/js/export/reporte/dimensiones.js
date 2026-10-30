export const FUENTE_ENCV = {
    texto: 'DANE, Encuesta Nacional de Calidad de Vida (ECV). Anexo FIES 2024.',
    url: 'https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/calidad-de-vida-ecv',
};

export const DIMENSIONES = {
    aporte_Vivienda_y_Servicios: {
        queMide: 'Tipo de vivienda, materiales de paredes y pisos, acueducto, alcantarillado, continuidad y tratamiento del agua, combustible para cocinar y tenencia de nevera.',
        porQue: 'Es la infraestructura donde se almacena, prepara y conserva el alimento. Sin refrigeración se pierden perecederos y se reduce la variedad; sin agua segura y saneamiento aumentan las infecciones que impiden aprovechar los nutrientes; cocinar con leña o carbón afecta la salud respiratoria y consume tiempo y dinero.',
        evidencia: 'Hogares con déficit habitacional: 40,4 %. Sin déficit: 19,5 %.',
    },
    aporte_Trabajo_e_Ingresos: {
        queMide: 'Actividad principal, ingreso mensual, tiempo de búsqueda de empleo, cotización a pensión, afiliación a riesgos laborales, tamaño de la empresa y horas trabajadas.',
        porQue: 'El ingreso es el medio principal para acceder a los alimentos y su estabilidad define si el hogar sostiene una dieta suficiente y variada. La informalidad y el desempleo vuelven ese ingreso volátil y obligan a recortar primero la calidad y la cantidad de comida.',
        evidencia: 'Jefe desempleado: 43,4 %. Jefe ocupado: 24,4 %.',
    },
    aporte_Salud_y_Discapacidad: {
        queMide: 'Afiliación al sistema de salud, régimen contributivo o subsidiado y seis dificultades funcionales: movilidad, uso de manos, cognición, autocuidado, comunicación y relaciones.',
        porQue: 'La enfermedad y la discapacidad elevan el gasto de bolsillo, reducen la capacidad de trabajo y exigen cuidados especiales. La afiliación refleja el tipo de vínculo laboral y la protección con que cuenta el hogar para enfrentar esos costos.',
        evidencia: 'Con discapacidad: 35,0 %. Sin discapacidad: 24,1 %. Contributivo: 12,8 %. Subsidiado: 37,2 %.',
    },
    aporte_Educacion: {
        queMide: 'Alfabetismo, asistencia escolar, nivel educativo alcanzado y acceso a subsidios educativos.',
        porQue: 'La educación del jefe incide en la capacidad de generar ingresos, acceder a información nutricional y adoptar prácticas de cuidado. También condiciona la trayectoria escolar de los niños, que es el principal mecanismo de salida de la pobreza.',
        evidencia: 'Jefe sin educación: 47,4 %. Jefe con educación superior: 12,7 %.',
    },
    aporte_Demografia: {
        queMide: 'Tamaño del hogar, sexo y edad de sus miembros y autorreconocimiento étnico.',
        porQue: 'Un hogar más grande reparte el mismo ingreso entre más personas. La presencia de menores de cinco años añade necesidades nutricionales y de cuidado, y la pertenencia étnica se asocia históricamente a mayor exclusión.',
        evidencia: 'Hogares de 5 personas o más: 35,2 %. Unipersonales: 22,4 %. Con menor de 5 años: 31,5 %.',
    },
    aporte_Desastres: {
        queMide: 'Eventos climáticos de los últimos doce meses —inundaciones, sequías, deslizamientos, vendavales o sismos— y sus efectos sobre el agua, los cultivos, los animales, la salud y los suelos.',
        porQue: 'Un evento extremo destruye activos, vivienda y cosecha, y obliga al hogar a vender bienes o reducir comidas para enfrentar la emergencia. En zonas rurales, la pérdida de la cosecha golpea directamente la disponibilidad de alimentos y el ingreso.',
        evidencia: 'Incluye pérdida de cultivos o animales y reducción del agua disponible (ECV 2025, P3174).',
    },
};
